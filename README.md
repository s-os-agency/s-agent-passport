# S/ Omni Model

The pinned Qwen2.5-Omni-7B weights, installer, private inference runtime and resource clients remain in this same GitHub repository. Only its name changed from `s-agent-passport` to `s-omni-model`; the repository ID, published release and all 29 release assets are unchanged.

- [Runtime and deployment requirements](s-agency/model-assets/runtime/README.md)
- [Pinned model lock](s-agency/model-assets/registry/omni-model.lock.json)
- [Published weights](https://github.com/s-os-agency/s-omni-model/releases/tag/qwen2.5-omni-7b-ae9e169-weights-v1)
- [Model registry and supporting assets](s-agency/model-assets/README.md)

Model paths and installer identity are preserved. The original `s-agent-passport` string stays in the pinned distribution manifest, lock and downloader so existing installations remain compatible. Do not create another repository at the old name, which would remove its redirects.

## Passport source

The existing Passport server is at [s-agent-passport-server](https://github.com/s-os-agency/s-agent-passport-server). An [isolated extraction branch](https://github.com/s-os-agency/s-agent-passport-server/tree/passport-source-separation) currently contains 171 unchanged source files. Twenty files containing prior personal-name content and one issuer configuration are held pending authorization. This partial copy is not deployable and does not replace the existing server.

The full prior layout and history remain untouched on this repository's [compatibility main branch](https://github.com/s-os-agency/s-omni-model/tree/main). Existing references to `/main/` and pinned commits continue to resolve. No original Passport source was deleted, and no existing server, database, credential, gateway or deployed connection was changed.

## Verified scope

The 29 release asset IDs, sizes and SHA-256 digests match the pre-rename values. The old manifest download URL still returns identical bytes. GPU inference and remote resource deployment remain unverified; repository organization does not change that status.

The publisher guard now recognizes the unchanged numeric repository ID after renaming, while retaining its original manifest identity and refusal to overwrite published assets. No model weights were re-uploaded. No software tests or deployment commands were run.

Implementation: OpenAI dot, 12 November 2026.
