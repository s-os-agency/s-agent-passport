"""Publish actual pinned model bytes as GitHub Release assets, never Git blobs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / "registry/omni-model.lock.json").read_text())
REPOSITORY = "s-os-agency/s-agent-passport"
TAG = "qwen2.5-omni-7b-ae9e169-weights-v1"
CHUNK_SIZE = 1_900_000_000  # GitHub requires each release asset < 2 GiB.
BLOCK = 8 * 1024 * 1024


def gh(*args, output=None):
    result = subprocess.run(["gh", *args], check=True, stdout=output or subprocess.PIPE,
                            timeout=2400, text=output is None)
    return result.stdout if output is None else None


def api(path):
    return json.loads(gh("api", path))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(BLOCK), b""):
            h.update(data)
    return h.hexdigest()


def main():
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise RuntimeError("Publish only inside the existing canonical repository.")
    repo = api(f"repos/{REPOSITORY}")
    if repo["private"]:
        raise RuntimeError("Only the existing public repository's free standard runner is allowed.")
    source = f"https://huggingface.co/api/models/{LOCK['repo_id']}/revision/{LOCK['revision']}?blobs=true"
    with urlopen(Request(source, headers={"User-Agent": "s-agency-model-distribution/1"}), timeout=60) as response:
        info = json.loads(response.read(5_000_000))
    if info["sha"] != LOCK["revision"]:
        raise RuntimeError("Hugging Face revision mismatch.")
    upstream = {entry["rfilename"]: entry for entry in info["siblings"]}
    names = list(LOCK["files"])
    if "NOTICE" in upstream and "NOTICE" not in names:
        names.append("NOTICE")
    selected = [upstream[name] for name in names]
    total = sum(entry["size"] for entry in selected)
    if total > LOCK["download_limit_bytes"]:
        raise RuntimeError("Snapshot exceeds the committed byte budget.")
    releases = api(f"repos/{REPOSITORY}/releases?per_page=100")
    matches = [release for release in releases if release["tag_name"] == TAG]
    if matches:
        release = matches[0]
        if not release["draft"]:
            raise RuntimeError("Release already published; never replace published weights.")
    else:
        notes = (f"Actual Qwen2.5-Omni-7B model weights and required tokenizer/configuration files.\n\n"
                 f"Upstream: {LOCK['source_url']}/tree/{LOCK['revision']}\n"
                 "Model license: Apache-2.0; the original LICENSE and model card are included.\n"
                 "Weights are unmodified; large files are split into losslessly reassembled parts.\n"
                 "Text/image/audio/video input; text/audio output. This release does not claim a live GPU endpoint.\n\n"
                 "Use s-agency/model-assets/runtime/download_from_github.py from this repository. "
                 "The distribution manifest records original and part hashes and download URLs.\n"
                 "Every asset was downloaded back from GitHub and matched before publication.\n"
                 f"Executing agent: OpenAI dot. Source commit: {os.environ['GITHUB_SHA']}.\n")
        gh("release", "create", TAG, "--repo", REPOSITORY, "--target", os.environ["GITHUB_SHA"],
           "--draft", "--title", "Qwen2.5-Omni-7B: actual model weights", "--notes", notes)
        release = next(r for r in api(f"repos/{REPOSITORY}/releases?per_page=100") if r["tag_name"] == TAG)
    release_id = release["id"]
    assets = {a["name"]: a for a in api(f"repos/{REPOSITORY}/releases/{release_id}/assets?per_page=100")}
    manifest = {"schema_version": 1, "repository": REPOSITORY, "tag": TAG,
                "repo_id": LOCK["repo_id"], "revision": LOCK["revision"],
                "license": LOCK["license"], "total_bytes": total,
                "source_commit": os.environ["GITHUB_SHA"], "files": [],
                "inference_observed": False,
                "published_by": "OpenAI dot", "github_roundtrip_verified": True}
    with tempfile.TemporaryDirectory(prefix="qwen-distribution-") as temp:
        work = Path(temp)
        if shutil.disk_usage(work).free < max(e["size"] for e in selected) + CHUNK_SIZE * 2 + 500_000_000:
            raise RuntimeError("Not enough ephemeral disk for one source shard and release readback.")

        def upload_and_readback(path, expected_hash):
            name = path.name
            if name not in assets:
                gh("release", "upload", TAG, str(path), "--repo", REPOSITORY)
                assets.update({a["name"]: a for a in api(f"repos/{REPOSITORY}/releases/{release_id}/assets?per_page=100")})
            asset = assets[name]
            if asset["size"] != path.stat().st_size or asset.get("digest") != f"sha256:{expected_hash}":
                raise RuntimeError(f"Existing GitHub asset differs: {name}; no overwrite allowed.")
            fetched = work / "readback.bin"
            with fetched.open("wb") as target:
                gh("api", "-H", "Accept: application/octet-stream", f"repos/{REPOSITORY}/releases/assets/{asset['id']}", output=target)
            if fetched.stat().st_size != asset["size"] or sha256(fetched) != expected_hash:
                raise RuntimeError(f"GitHub roundtrip integrity failure: {name}")
            fetched.unlink()
            print(f"GITHUB_BYTES_VERIFIED {name} {asset['size']} {expected_hash}", flush=True)
            return {"name": name, "bytes": asset["size"], "sha256": expected_hash,
                    "url": f"https://github.com/{REPOSITORY}/releases/download/{TAG}/{quote(name)}"}

        for entry in selected:
            name = entry["rfilename"]
            if Path(name).name != name:
                raise RuntimeError("Unexpected nested upstream file.")
            original = work / (name + ".source")
            url = f"https://huggingface.co/{LOCK['repo_id']}/resolve/{LOCK['revision']}/{quote(name)}?download=true"
            print(f"FETCH_UPSTREAM {name} {entry['size']}", flush=True)
            subprocess.run(["curl", "-q", "--fail", "--location", "--silent", "--show-error",
                            "--retry", "3", "--connect-timeout", "30", "--max-time", "2400",
                            "--output", str(original), url], check=True, timeout=2450)
            if original.stat().st_size != entry["size"]:
                raise RuntimeError(f"Upstream byte count mismatch: {name}")
            checksum = sha256(original)
            lfs = entry.get("lfs")
            if lfs and checksum != lfs["sha256"]:
                raise RuntimeError(f"Upstream SHA-256 mismatch: {name}")
            if not lfs:
                h = hashlib.sha1(f"blob {entry['size']}\0".encode())
                h.update(original.read_bytes())
                if h.hexdigest() != entry["blobId"]:
                    raise RuntimeError(f"Upstream Git blob mismatch: {name}")
            record = {"path": name, "bytes": entry["size"], "sha256": checksum, "parts": []}
            with original.open("rb") as stream:
                index = 0
                while stream.tell() < entry["size"]:
                    part_name = name if entry["size"] < CHUNK_SIZE else f"{name}.part{index:03d}"
                    part = work / part_name
                    remaining = min(CHUNK_SIZE, entry["size"] - stream.tell())
                    ph = hashlib.sha256()
                    with part.open("wb") as output:
                        while remaining:
                            data = stream.read(min(BLOCK, remaining))
                            if not data:
                                raise RuntimeError("Unexpected end of upstream file.")
                            output.write(data)
                            ph.update(data)
                            remaining -= len(data)
                    record["parts"].append(upload_and_readback(part, ph.hexdigest()))
                    part.unlink()
                    index += 1
            original.unlink()
            manifest["files"].append(record)
        manifest["verified_at"] = datetime.now(timezone.utc).isoformat()
        manifest_path = work / "distribution-manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        manifest_hash = sha256(manifest_path)
        upload_and_readback(manifest_path, manifest_hash)
        gh("release", "edit", TAG, "--repo", REPOSITORY, "--draft=false", "--latest=false")
        published = api(f"repos/{REPOSITORY}/releases/tags/{TAG}")
        if published["draft"] or len(published["assets"]) != sum(len(f["parts"]) for f in manifest["files"]) + 1:
            raise RuntimeError("Published release is incomplete.")
        receipt = {"release_url": published["html_url"], "manifest_sha256": manifest_hash,
                   "total_original_bytes": total, "asset_count": len(published["assets"]),
                   "github_roundtrip_verified": True, "inference_observed": False}
        print("PUBLISHED_MODEL_RECEIPT " + json.dumps(receipt), flush=True)
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
            summary.write("# Actual model weights published\n\n" + json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
