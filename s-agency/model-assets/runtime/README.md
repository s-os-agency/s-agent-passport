# Shared Omni model runtime

This package turns the existing model registry into a downloadable, pinned runtime
and a small client that other resources can reuse. **Source prepared; no deployed
GPU service or generated result has been observed yet.**

## Model choice

The initial model is [Qwen/Qwen2.5-Omni-7B](https://huggingface.co/Qwen/Qwen2.5-Omni-7B),
locked to `ae9e1690543ffd5c0221dc27f79834d0294cba00`. It accepts text, images, audio,
and video, and returns text or speech. It does not generate images or videos.

The 7B release has an Apache-2.0 license and a roughly 22.4 GB snapshot. The smaller
3B release has a research license, so it is not the default commercial-distribution
choice. Qwen3-Omni-30B-A3B-Instruct offers broader language support but a roughly
70.5 GB snapshot and substantially higher GPU requirements. This package chooses
the smaller permissively licensed Omni deployment, not the newest/largest model.
Arabic speech generation is not promised by this package.

The pinned official weights stay on Hugging Face and the selected GPU host, not in
Git history, Git LFS billing, every resource repository, or browser downloads.
The downloader keeps the original model card and license with the weights.

## Deployment requirements and current blocker

- An already-authorized Linux CUDA GPU host, Python 3.11, and FFmpeg.
- Plan for a 48 GB GPU for short multimodal inputs, at least 35 GB free model disk,
  and additional disk for Python/CUDA dependencies. The model card reports 31.11 GB
  theoretical BF16 memory for a 15-second video with FlashAttention 2 and says
  real use is generally at least 1.2 times higher. This is not a capacity guarantee.
- The default SDPA backend needs no compiled FlashAttention install; its actual
  memory requirement may be higher. Shorten inputs if capacity is insufficient.
- One shared GPU process. Existing CPU services and Cloudflare Workers call it
  through the client; they do not load this model themselves.
- Existing owner-authorized Passport scope, HTTPS gateway authentication,
  revocation, rate limits, and request size limits before remote access.

No suitable GPU host or scoped gateway was available during source preparation.
No GPU was rented, no model weights were downloaded into GitHub, no credentials
were created, and no production routes were changed. Existing model activation
rules and access rights remain in force.

## Download once on the selected host

Run from this directory after selecting the existing authorized GPU host:

```sh
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python download_model.py --cache-dir /srv/s-omni/cache --receipt /srv/s-omni/download.json
```

The downloader requests only the explicit locked files from the official public
repository, sends no Hugging Face token, checks revision, sizes and LFS SHA-256
digests, and saves a local receipt. It refuses a snapshot larger than 26 GB and
checks available disk before downloading. Reuse this cache rather than duplicating
the model for each resource. The receipt contains host-local paths; keep it private.

The top-level Python package versions are pinned; transitive dependencies are not
a complete lockfile. Host compatibility and inference remain unverified here.

## Run the private worker

```sh
python serve.py --receipt /srv/s-omni/download.json
```

It binds **127.0.0.1:8091 only**. There is no public bind option, no new authentication
secret, and no bypass of Passport. An existing approved gateway on the same host
must enforce identity, allowed model scope, revocation and rate limits before
forwarding external requests. Do not publish this raw loopback service directly.
Put it behind that gateway only after the real target and existing access controls
have been verified. Use one process per model copy.

Startup verifies every downloaded file against the receipt, then loads the local
snapshot with `trust_remote_code=False` and safetensors. The official auxiliary
speaker tensor file is included, loaded by Transformers with `weights_only=True`.
No remote model Python code is downloaded or executed.

`GET /healthz` reports ready only after model loading. `POST /v1/generate` accepts:

```json
{
  "prompt": "Describe the attached image in one sentence.",
  "media": [{"mime_type": "image/jpeg", "data_base64": "BASE64_IMAGE_BYTES"}],
  "audio_output": false,
  "use_audio_in_video": false,
  "max_tokens": 256
}
```

Media are bytes, never remote URLs or local paths supplied by callers. Limits are
24 MiB per JSON request, 8 MiB per file, 16 MiB combined decoded media, four media
items, one video, 15-second video, 30-second audio, 4-megapixel images and 1080p
video. The encoded prompt is limited to 12,000 tokens and output to 512 tokens.
Generated speech is a 24 kHz WAV encoded in the `audio.data_base64` response field.
This first version is single-request, non-streaming and does not keep conversation
history. It does not persist prompts or uploaded media. Temporary inputs are removed.

## Use from the existing resources

Copy/import `client.mjs` into a server-side Node 20+ or Worker resource at a pinned
GitHub commit. Configure its already-authorized gateway URL and scoped credential
in the provider secret store, never in a frontend, repository or log.

```js
import { generateOmni } from './client.mjs';
const result = await generateOmni({
  baseURL: process.env.S_OMNI_BASE_URL,
  token: process.env.S_OMNI_BEARER_TOKEN,
  prompt: 'Summarize this text in one sentence: The project is ready for review.',
});
```

`routeOmni` returns the existing LLM router's `success/provider/model/text` shape.
No fallback provider is silently selected, and the client verifies the returned
model revision. Existing `s-cloudflare-workers`, `llm-council` and other resources
should keep their working routes until this endpoint has a real operating receipt.
The package does not claim those resources are already connected.

After the service is genuinely running, a real local request can save its result:

```sh
python request.py --prompt 'Summarize the shared model service in one sentence.' --output outputs/result-001.json
python request.py --prompt 'Describe this image.' --media ./image.jpg --audio-output --output outputs/result-002.json
```

For remote use, set `S_OMNI_BASE_URL` to the verified approved HTTPS gateway and
provide `S_OMNI_BEARER_TOKEN` from the existing secret store. Only send media and
prompts already authorized for that destination. The client follows no redirects
and does not retry a possibly completed request.

## Operation evidence and rollback

Before calling this live, retain the provider's deployment receipt, model download
receipt, ready response and an actual generated result with request ID and pinned
model revision. Download completion is not inference evidence.

No software tests or test scaffolding were added or run. Preparation evidence is
source and configuration inspection only. The executing assistant prepared this
package on 2026-11-11. No real runtime response is included or fabricated.

Rollback is to stop this optional worker and keep existing resource routes. No
database migrations, production auth changes or destructive actions are required.

## Sources

- [Pinned model and license](https://huggingface.co/Qwen/Qwen2.5-Omni-7B/tree/ae9e1690543ffd5c0221dc27f79834d0294cba00)
- [Official usage and memory guidance](https://huggingface.co/Qwen/Qwen2.5-Omni-7B#quickstart)
- [Transformers model implementation](https://github.com/huggingface/transformers/blob/v4.57.1/src/transformers/models/qwen2_5_omni/modeling_qwen2_5_omni.py)
- [Qwen3 Omni alternative](https://huggingface.co/Qwen/Qwen3-Omni-30B-A3B-Instruct)
