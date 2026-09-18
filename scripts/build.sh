#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

python tools/theme_tool.py validate
pio run -e hakctel
mkdir -p dist
# bin/platformio-pre.py replaces PROGNAME with firmware-<env>-<version>, so there is no
# plain firmware.bin to copy. Take the app image, never the merged *.factory.bin.
firmware_bin="$(find .pio/build/hakctel -maxdepth 1 -name 'firmware-hakctel-*.bin' ! -name '*.factory.bin' | sort | head -n1)"
if [[ ! -f "$firmware_bin" ]]; then
  printf '%s\n' "No hakcTEL firmware image in .pio/build/hakctel" >&2
  exit 1
fi
cp "$firmware_bin" dist/hakctel-firmware.bin
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
