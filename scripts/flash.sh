#!/usr/bin/env bash
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
pio run -e hakctel -t upload --upload-port "$port"
