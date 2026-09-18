#!/usr/bin/env bash
# Full-chip erase over USB serial.
#
# The browser installer (site/manifest.json) and scripts/flash.sh both write only four
# regions: bootloader@0x0, partitions@0x8000, boot_app0@0xe000, firmware(app0)@0x10000.
# The littlefs/spiffs filesystem lives at 0xc90000 (see default_16MB.csv) and is never
# touched by either path, "erase" checkbox or not. Old node database, message history,
# and any drafts/queued messages from a previous firmware survive every browser reflash.
# If a unit keeps retrying an old message or shows garbled message history after a clean
# install, that stale filesystem -- not the new firmware -- is almost always why. This
# wipes the whole chip so the next boot starts from nothing.
set -euo pipefail

if [[ $# -ne 1 ]]; then
    printf '%s\n' "Usage: $0 /dev/ttyACM0" >&2
    exit 2
fi

port="$1"
if [[ ! -e "$port" ]]; then
    printf 'Serial port does not exist: %s\n' "$port" >&2
    exit 2
fi

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

# esptool's dependencies (rich_click, etc.) live in PlatformIO's own penv, not this
# project's venv -- same core_dir lookup scripts/build.sh already uses to find
# boot_app0.bin. `esptool.py` run directly self-shadows the `esptool/` package sitting
# next to it, so invoke it as a module from PlatformIO's own interpreter instead.
core_dir="$(pio system info --json-output | python -c 'import json,sys; print(json.load(sys.stdin)["core_dir"]["value"])')"
penv_python="$core_dir/penv/bin/python"
if [[ ! -x "$penv_python" ]]; then
    printf 'PlatformIO penv not found at %s -- run ./installer.sh and ./scripts/build.sh at least once first.\n' "$penv_python" >&2
    exit 1
fi

printf '%s\n' "Erasing entire flash chip on $port -- this removes ALL saved state (node database, message history, drafts, theme selection, radio config)."
(cd "$core_dir/packages/tool-esptoolpy" && "$penv_python" -m esptool --chip esp32s3 --port "$port" erase_flash)

printf '%s\n' "Erased. Reflash with ./scripts/flash.sh $port or the browser installer."
