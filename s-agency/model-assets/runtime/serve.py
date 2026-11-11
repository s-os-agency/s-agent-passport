"""Loopback-only Omni worker. Publish only behind the existing authorized gateway."""
import argparse
import base64
import binascii
import io
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import tempfile
import time
import uuid

from download_model import digest, load_lock

MAX_BODY = 24 * 1024 * 1024
MAX_MEDIA_BYTES = 8 * 1024 * 1024
SYSTEM_PROMPT = (
    "You are Qwen, a virtual human developed by the Qwen Team, Alibaba Group, "
    "capable of perceiving auditory and visual inputs, as well as generating text and speech."
)
MEDIA_TYPES = {
    "image/png": ("image", ".png"), "image/jpeg": ("image", ".jpg"),
    "audio/wav": ("audio", ".wav"), "audio/mpeg": ("audio", ".mp3"),
    "video/mp4": ("video", ".mp4"),
}


def validate_request(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object.")
    if set(payload) - {"prompt", "media", "audio_output", "use_audio_in_video", "max_tokens"}:
        raise ValueError("Unsupported request fields.")
    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str) or not 1 <= len(prompt.strip()) <= 16000:
        raise ValueError("prompt must contain 1 to 16000 characters.")
    for key in ("audio_output", "use_audio_in_video"):
        if key in payload and type(payload[key]) is not bool:
            raise ValueError(f"{key} must be boolean.")
    maximum = payload.get("max_tokens", 256)
    if type(maximum) is not int or not 1 <= maximum <= 512:
        raise ValueError("max_tokens must be between 1 and 512.")
    media = payload.get("media", [])
    if not isinstance(media, list) or len(media) > 4:
        raise ValueError("media must be an array with at most four items.")
    return prompt, media, maximum


def materialize_media(items, directory):
    """Accept bytes only: never fetch caller URLs or read caller file paths."""
    import av
    from PIL import Image

    parts = []
    total = 0
    video_count = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != {"mime_type", "data_base64"}:
            raise ValueError("Each media item needs mime_type and data_base64 only.")
        mime = item["mime_type"]
        if not isinstance(mime, str) or mime not in MEDIA_TYPES:
            raise ValueError("Unsupported media type.")
        encoded = item["data_base64"]
        if not isinstance(encoded, str) or len(encoded) > MAX_MEDIA_BYTES * 4 // 3 + 4:
            raise ValueError("Media exceeds the 8 MiB per-file limit.")
        try:
            data = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Invalid base64 media.") from exc
        total += len(data)
        if not data or len(data) > MAX_MEDIA_BYTES or total > 16 * 1024 * 1024:
            raise ValueError("Media is empty or exceeds the size limit.")
        kind, suffix = MEDIA_TYPES[mime]
        if kind == "image":
            with Image.open(io.BytesIO(data)) as image:
                if image.width * image.height > 4_000_000:
                    raise ValueError("Images are limited to 4 megapixels.")
                image.verify()
        else:
            with av.open(io.BytesIO(data)) as container:
                limit = 15 if kind == "video" else 30
                if container.duration is None or container.duration <= 0:
                    raise ValueError("Media must declare a valid duration.")
                if container.duration / av.time_base > limit:
                    raise ValueError(f"{kind} exceeds the {limit}-second limit.")
                streams = container.streams.video if kind == "video" else container.streams.audio
                if not streams:
                    raise ValueError("Media does not contain the declared stream type.")
                if kind == "video":
                    video_count += 1
                    if video_count > 1:
                        raise ValueError("Only one video is allowed per request.")
                    stream = streams[0]
                    if stream.width * stream.height > 1920 * 1080:
                        raise ValueError("Video resolution is limited to 1920x1080 pixels.")
        path = directory / f"input-{index}{suffix}"
        path.write_bytes(data)
        part = {"type": kind, kind: str(path)}
        if kind == "image":
            part["max_pixels"] = 448 * 448
        if kind == "video":
            part.update({"fps": 1.0, "max_pixels": 448 * 448})
        parts.append(part)
    return parts


class OmniRuntime:
    def __init__(self, receipt_path, attention):
        import torch
        from transformers import Qwen2_5OmniForConditionalGeneration, Qwen2_5OmniProcessor

        self.lock = load_lock()
        if not torch.cuda.is_available():
            raise RuntimeError("A CUDA GPU host is required; CPU fallback is disabled.")
        receipt = json.loads(Path(receipt_path).read_text())
        if any(receipt.get(key) != self.lock[key] for key in ("repo_id", "revision")):
            raise RuntimeError("Download receipt does not match the pinned model.")
        model_path = Path(receipt["model_path"]).resolve()
        for name in self.lock["files"]:
            if digest(model_path / name) != receipt["sha256"].get(name):
                raise RuntimeError(f"Downloaded file integrity mismatch: {name}")
        # Local snapshot path also pins the auxiliary speaker file. No remote code.
        self.model = Qwen2_5OmniForConditionalGeneration.from_pretrained(
            str(model_path), torch_dtype=torch.bfloat16, device_map="auto",
            attn_implementation=attention, local_files_only=True,
            trust_remote_code=False, use_safetensors=True,
        )
        self.model.eval()
        self.processor = Qwen2_5OmniProcessor.from_pretrained(
            str(model_path), local_files_only=True, trust_remote_code=False
        )

    def generate(self, payload):
        import torch
        import soundfile
        from qwen_omni_utils import process_mm_info

        prompt, media, maximum = validate_request(payload)
        audio_output = payload.get("audio_output", False)
        use_audio = payload.get("use_audio_in_video", False)
        with tempfile.TemporaryDirectory(prefix="s-omni-") as temporary:
            parts = materialize_media(media, Path(temporary))
            parts.append({"type": "text", "text": prompt})
            conversation = [
                {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
                {"role": "user", "content": parts},
            ]
            text = self.processor.apply_chat_template(
                conversation, add_generation_prompt=True, tokenize=False
            )
            audios, images, videos = process_mm_info(conversation, use_audio_in_video=use_audio)
            inputs = self.processor(
                text=text, audio=audios, images=images, videos=videos,
                return_tensors="pt", padding=True, use_audio_in_video=use_audio,
            ).to(self.model.device).to(self.model.dtype)
            if inputs["input_ids"].shape[1] > 12000:
                raise ValueError("Encoded input exceeds the 12000-token limit.")
            with torch.inference_mode():
                generated = self.model.generate(
                    **inputs, use_audio_in_video=use_audio, return_audio=audio_output,
                    thinker_max_new_tokens=maximum, talker_max_new_tokens=1024,
                    thinker_do_sample=False,
                )
            ids, waveform = generated if audio_output else (generated, None)
            # Return only new output, never echo the prompt or system message.
            response_text = self.processor.batch_decode(
                ids[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )[0]
            result = {
                "id": str(uuid.uuid4()), "model": self.lock["repo_id"],
                "revision": self.lock["revision"], "text": response_text,
            }
            if waveform is not None:
                audio = io.BytesIO()
                soundfile.write(audio, waveform.reshape(-1).detach().cpu().numpy(),
                                24000, format="WAV")
                result["audio"] = {"mime_type": "audio/wav", "sample_rate": 24000,
                                   "data_base64": base64.b64encode(audio.getvalue()).decode()}
            return result


def make_handler(runtime):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(30)

        def log_message(self, *args):
            pass  # Do not log request bodies, prompts, URLs, or media.

        def respond(self, status, payload):
            data = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(data)
            self.close_connection = True

        def do_GET(self):
            if self.path != "/healthz":
                self.respond(404, {"error": "Not found"})
                return
            self.respond(200, {"ready": True, "model": runtime.lock["repo_id"],
                               "revision": runtime.lock["revision"]})

        def do_POST(self):
            if self.path != "/v1/generate":
                self.respond(404, {"error": "Not found"})
                return
            if self.headers.get("Transfer-Encoding"):
                self.respond(400, {"error": "Chunked requests are not supported"})
                return
            if self.headers.get_content_type() != "application/json":
                self.respond(415, {"error": "Use application/json"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_BODY:
                    self.respond(413, {"error": "Request exceeds the 24 MiB limit"})
                    return
                data = self.rfile.read(length)
                if len(data) != length:
                    raise ValueError("Incomplete request")
                payload = json.loads(data)
                started = time.monotonic()
                result = runtime.generate(payload)
                result["elapsed_seconds"] = round(time.monotonic() - started, 3)
                self.respond(200, result)
            except (ValueError, UnicodeError):
                self.respond(400, {"error": "Invalid request or unsupported media"})
            except Exception:
                self.respond(503, {"error": "Generation failed; inspect GPU capacity and input media"})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--port", type=int, default=8091)
    parser.add_argument("--attention", choices=["sdpa", "flash_attention_2"], default="sdpa")
    args = parser.parse_args()
    runtime = OmniRuntime(args.receipt, args.attention)
    # A single process handles one generation at a time: no parallel model copies.
    server = HTTPServer(("127.0.0.1", args.port), make_handler(runtime))
    print(json.dumps({"listening": f"http://127.0.0.1:{args.port}",
                      "model": runtime.lock["repo_id"], "ready": True}), flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
