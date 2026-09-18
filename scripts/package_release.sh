#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

./scripts/build.sh
python tools/theme_tool.py catalog --output site/themes/catalog.json
python tools/theme_tool.py preview

# The browser installer fetches these over XHR, so they must be same-origin with the page.
# GitHub release assets send no Access-Control-Allow-Origin, which fails the install with
# "Failed to fetch", so site/manifest.json points at /firmware/ and the site serves them.
mkdir -p site/firmware
cp dist/hakctel-bootloader.bin dist/hakctel-partitions.bin dist/hakctel-boot-app0.bin dist/hakctel-firmware.bin site/firmware/

printf '%s\n' "Release assets are ready in dist/ and site/."
