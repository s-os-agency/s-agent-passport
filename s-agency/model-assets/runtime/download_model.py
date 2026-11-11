"""Download the pinned official snapshot into the selected host's HF cache."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from datetime import datetime, timezone

LOCK = Path(__file__).resolve().parents[1] / "registry" / "omni-model.lock.json"


def load_lock():
    return json.loads(LOCK.read_text())


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    from huggingface_hub import HfApi, snapshot_download

    lock = load_lock()
    cache = Path(args.cache_dir).expanduser().resolve()
    cache.mkdir(parents=True, exist_ok=True)
    # Public model: never send a saved HF token for this download.
    info = HfApi(token=False).model_info(
        lock["repo_id"], revision=lock["revision"], files_metadata=True
    )
    if info.sha != lock["revision"]:
        raise RuntimeError("Upstream revision does not match the committed lock.")
    files = {entry.rfilename: entry for entry in info.siblings}
    selected = [files[name] for name in lock["files"]]
    if any(item.size is None for item in selected):
        raise RuntimeError("Upstream did not provide complete file sizes.")
    size = sum(item.size for item in selected)
    if size > lock["download_limit_bytes"]:
        raise RuntimeError("Pinned snapshot exceeds the package download budget.")
    if shutil.disk_usage(cache).free < size + 2_000_000_000:
        raise RuntimeError("Not enough free disk for the complete pinned snapshot.")
    model_path = Path(snapshot_download(
        lock["repo_id"], revision=lock["revision"], cache_dir=str(cache),
        allow_patterns=lock["files"], token=False, max_workers=4,
    ))
    checksums = {}
    for item in selected:
        path = model_path / item.rfilename
        if path.stat().st_size != item.size:
            raise RuntimeError(f"File size mismatch: {item.rfilename}")
        checksum = digest(path)
        if item.lfs is not None and checksum != item.lfs.sha256:
            raise RuntimeError(f"SHA-256 mismatch: {item.rfilename}")
        checksums[item.rfilename] = checksum
    receipt = {
        "repo_id": lock["repo_id"], "revision": lock["revision"],
        "model_path": str(model_path), "downloaded_bytes": size,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "sha256": checksums, "inference_observed": False,
    }
    target = Path(args.receipt).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2) + "\n")
    os.replace(temporary, target)
    print(json.dumps({"receipt": str(target), "model_path": str(model_path),
                      "downloaded_bytes": size}))


if __name__ == "__main__":
    main()
