#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_CATALOG = "https://hakctel.hakc.ai/themes/catalog.json"
MAX_CATALOG_BYTES = 256 * 1024
MAX_THEME_BYTES = 8192


def download(url: str, limit: int) -> bytes:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("only HTTPS URLs are accepted")
    request = urllib.request.Request(url, headers={"User-Agent": "hakcTEL-theme-sync/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"download exceeds {limit} bytes")
    return data


def install(sd_root: Path, theme_id: str, catalog_url: str) -> Path:
    if not sd_root.is_dir():
        raise ValueError("SD root does not exist or is not a directory")
    catalog = json.loads(download(catalog_url, MAX_CATALOG_BYTES))
    match = next((item for item in catalog.get("themes", []) if item.get("id") == theme_id), None)
    if not match:
        raise ValueError(f"theme not found: {theme_id}")
    theme_url = urllib.parse.urljoin(catalog_url, match["theme"])
    payload = download(theme_url, MAX_THEME_BYTES)
    digest = hashlib.sha256(payload).hexdigest()
    if digest != match.get("sha256"):
        raise ValueError("theme checksum mismatch")

    destination = sd_root / "hakctel" / "themes" / theme_id / "theme.ini"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temp:
        temp.write(payload)
        temp_path = Path(temp.name)
    os.replace(temp_path, destination)
    active = sd_root / "hakctel" / "active-theme.txt"
    active.write_text(theme_id + "\n", encoding="ascii")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a verified hakcTEL theme onto a mounted microSD card")
    parser.add_argument("--sd-root", type=Path, required=True)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--catalog", default=DEFAULT_CATALOG)
    args = parser.parse_args()
    path = install(args.sd_root.resolve(), args.theme, args.catalog)
    print(f"installed {args.theme} at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
