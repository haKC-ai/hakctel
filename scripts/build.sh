#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

python tools/theme_tool.py validate
pio run -e hakctel
mkdir -p dist
cp .pio/build/hakctel/firmware.bin dist/hakctel-firmware.bin
cp .pio/build/hakctel/bootloader.bin dist/hakctel-bootloader.bin
cp .pio/build/hakctel/partitions.bin dist/hakctel-partitions.bin
core_dir="$(pio system info --json-output | python -c 'import json,sys; print(json.load(sys.stdin)["core_dir"]["value"])')"
boot_app0="$core_dir/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin"
if [[ ! -f "$boot_app0" ]]; then
  printf '%s\n' "Missing framework boot_app0.bin at $boot_app0" >&2
  exit 1
fi
cp "$boot_app0" dist/hakctel-boot-app0.bin

printf '%s\n' "Built dist/hakctel-firmware.bin"
