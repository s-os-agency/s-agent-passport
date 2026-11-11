"""Install actual model weights from GitHub Releases without contacting Hugging Face."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

LOCK_PATH = Path(__file__).resolve().parents[1] / "registry/omni-model.lock.json"
REPOSITORY = "s-os-agency/s-agent-passport"
TAG = "qwen2.5-omni-7b-ae9e169-weights-v1"
BASE = f"https://github.com/{REPOSITORY}/releases/download/{TAG}/"
BLOCK = 8 * 1024 * 1024


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(BLOCK), b""):
            h.update(data)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    lock = json.loads(LOCK_PATH.read_text())
    distribution = lock.get("github_distribution", {})
    expected = distribution.get("manifest_sha256")
    if not expected or distribution.get("tag") != TAG:
        raise RuntimeError("GitHub weights release is not yet finalized in this source revision.")
    with urlopen(Request(BASE + "distribution-manifest.json", headers={"User-Agent": "s-agency-model-distribution/1"}), timeout=60) as response:
        raw = response.read(2_000_000)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError("Distribution manifest does not match the committed SHA-256.")
    manifest = json.loads(raw)
    if (manifest["repository"], manifest["tag"], manifest["repo_id"], manifest["revision"]) != (
            REPOSITORY, TAG, lock["repo_id"], lock["revision"]):
        raise RuntimeError("Distribution identity mismatch.")
    if manifest["total_bytes"] > lock["download_limit_bytes"]:
        raise RuntimeError("Distribution exceeds committed disk budget.")
    names = [entry["path"] for entry in manifest["files"]]
    if len(names) != len(set(names)) or not set(lock["files"]).issubset(names):
        raise RuntimeError("Distribution is incomplete or has duplicate paths.")
    if sum(entry["bytes"] for entry in manifest["files"]) != manifest["total_bytes"]:
        raise RuntimeError("Distribution byte total is inconsistent.")
    target = Path(args.model_dir).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    needed = sum(entry["bytes"] for entry in manifest["files"]
                 if not (target / entry["path"]).is_file())
    if shutil.disk_usage(target).free < needed + 2_000_000_000:
        raise RuntimeError("Not enough free disk for the complete model.")
    checksums = {}
    for entry in manifest["files"]:
        name = entry["path"]
        if Path(name).name != name or name in {".", ".."}:
            raise RuntimeError("Unsafe model path in manifest.")
        path = target / name
        if path.is_symlink():
            raise RuntimeError("Refusing to replace a symbolic link.")
        if path.exists():
            if path.stat().st_size != entry["bytes"] or digest(path) != entry["sha256"]:
                raise RuntimeError(f"Existing model file differs: {name}; refusing to overwrite it.")
        else:
            temporary = path.with_name(path.name + ".download")
            if temporary.exists() or temporary.is_symlink():
                raise RuntimeError(f"Unfinished download exists: {temporary}; move it aside before resuming.")
            whole = hashlib.sha256()
            written = 0
            try:
                with temporary.open("xb") as output:
                    for part in entry["parts"]:
                        url = part["url"]
                        if not url.startswith(BASE) or urlparse(url).hostname != "github.com":
                            raise RuntimeError("Unexpected asset origin.")
                        ph = hashlib.sha256()
                        count = 0
                        with urlopen(Request(url, headers={"User-Agent": "s-agency-model-distribution/1"}), timeout=180) as response:
                            while True:
                                data = response.read(min(BLOCK, part["bytes"] - count + 1))
                                if not data:
                                    break
                                count += len(data)
                                if count > part["bytes"]:
                                    raise RuntimeError("Asset exceeds its declared byte count.")
                                output.write(data)
                                ph.update(data)
                                whole.update(data)
                        if count != part["bytes"] or ph.hexdigest() != part["sha256"]:
                            raise RuntimeError(f"GitHub asset integrity mismatch: {part['name']}")
                        written += count
                if written != entry["bytes"] or whole.hexdigest() != entry["sha256"]:
                    raise RuntimeError(f"Reconstructed model file mismatch: {name}")
                os.replace(temporary, path)
            except Exception:
                temporary.unlink(missing_ok=True)
                raise
        checksums[name] = entry["sha256"]
        print(f"INSTALLED {name} {entry['bytes']}", flush=True)
    receipt = {"repo_id": lock["repo_id"], "revision": lock["revision"],
               "model_path": str(target), "downloaded_bytes": manifest["total_bytes"],
               "verified_at": datetime.now(timezone.utc).isoformat(), "sha256": checksums,
               "source": "github_release", "release_url": distribution["release_url"],
               "inference_observed": False}
    receipt_path = Path(args.receipt).expanduser().resolve()
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("x") as output:
        output.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"model_path": str(target), "receipt": str(receipt_path),
                      "downloaded_bytes": manifest["total_bytes"]}))


if __name__ == "__main__":
    main()
