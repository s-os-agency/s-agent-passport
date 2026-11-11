"""Send a real request to the authorized Omni gateway; no mock output or retries."""
import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from download_model import load_lock


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Gateway redirects are not allowed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--media", action="append", default=[])
    parser.add_argument("--audio-output", action="store_true")
    parser.add_argument("--use-audio-in-video", action="store_true")
    parser.add_argument("--output", required=True, help="New JSON result file; never overwritten")
    args = parser.parse_args()
    if Path(args.output).exists():
        raise RuntimeError("Output file already exists; choose a new result filename.")
    url = os.environ.get("S_OMNI_BASE_URL", "http://127.0.0.1:8091").rstrip("/")
    parsed = urllib.parse.urlsplit(url)
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise RuntimeError("Gateway URL must not contain credentials, query, or fragment.")
    if parsed.scheme != "https" and not (local and parsed.scheme == "http"):
        raise RuntimeError("Remote gateway must use HTTPS.")
    token = os.environ.get("S_OMNI_BEARER_TOKEN")
    if not local and not token:
        raise RuntimeError("Set the existing gateway's scoped authorization token.")
    if len(args.media) > 4:
        raise RuntimeError("At most four media files are supported.")
    media = []
    for filename in args.media:
        path = Path(filename)
        if path.stat().st_size > 8 * 1024 * 1024:
            raise RuntimeError("Media files must not exceed 8 MiB each.")
        mime = mimetypes.guess_type(path.name)[0]
        if mime in {"audio/x-wav", "audio/vnd.wave"}:
            mime = "audio/wav"
        media.append({"mime_type": mime, "data_base64": base64.b64encode(path.read_bytes()).decode()})
    payload = {"prompt": args.prompt, "media": media, "audio_output": args.audio_output,
               "use_audio_in_video": args.use_audio_in_video, "max_tokens": 256}
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url + "/v1/generate", json.dumps(payload).encode(), headers)
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=180) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Omni gateway returned HTTP {exc.code}.") from None
    lock = load_lock()
    if result.get("model") != lock["repo_id"] or result.get("revision") != lock["revision"]:
        raise RuntimeError("Response does not match the committed model lock.")
    if not isinstance(result.get("text"), str) or not result.get("id"):
        raise RuntimeError("Gateway response is missing the result or request ID.")
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write("\n")
    print(json.dumps({"result_file": str(target), "request_id": result["id"],
                      "model": result["model"]}))


if __name__ == "__main__":
    main()
