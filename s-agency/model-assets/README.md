# Agency Model Assets v0.1

This folder is the canonical registry for Agency model assets.

## Control Model

- GitHub is the source of truth.
- Google Sheets is the operating workbook.
- The owned knowledge graph renderer is the visual relationship map.
- Supabase is a prepared system mirror, not the canonical record.
- No model asset becomes runtime-active without owner approval and a passport scope.

## Connected Workbook

https://docs.google.com/spreadsheets/d/1yt4NBzqHKiwjZDDbcPqPh78pw1_yOMwCYImVl48eJjo/edit

## Files

- `registry/model-assets.v0.1.json`: governed Hugging Face model assets.
- `registry/advisory-skills.v0.1.json`: advisory skills used to evaluate and route assets.
- `graph/knowledge-graph.v0.1.json`: graph nodes and edges for the Agency control map.
- `supabase/s_agency_model_assets.prepared.sql`: prepared Supabase/Postgres mirror contract.

## Activation Status

The first approved runtime-ready assets are:

- `LiquidAI/LFM2.5-2.6B`
- `openai/whisper-large-v3`
- `sentence-transformers/all-MiniLM-L6-v2`

High-risk visual/audio/video assets stay `registry_only` until owner-reviewed.


## Shared any-to-any distribution

[Omni runtime and resource client](runtime/README.md) packages the pinned
`Qwen/Qwen2.5-Omni-7B` model for one GPU host and multiple client resources.
The [model lock](registry/omni-model.lock.json) records its exact upstream revision.
Actual model weights are published in the [GitHub Release](https://github.com/s-os-agency/s-agent-passport/releases/tag/qwen2.5-omni-7b-ae9e169-weights-v1).
The installer downloads and reconstructs these bytes from GitHub, with SHA-256
verification. GPU inference and remote resource connections are not yet deployed
or verified. Existing activation permissions are unchanged.
