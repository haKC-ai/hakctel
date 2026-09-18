#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
venv_dir="$repo_dir/.venv-hakctel"
python_bin="${PYTHON_BIN:-python3}"

"$python_bin" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else "Python 3.11 or newer is required")'
"$python_bin" -m venv "$venv_dir"
"$venv_dir/bin/python" -m pip install --upgrade pip
"$venv_dir/bin/python" -m pip install -r "$repo_dir/requirements.txt"

printf '%s\n' "hakcTEL tools installed in $venv_dir"
printf '%s\n' "Build: source .venv-hakctel/bin/activate && ./scripts/build.sh"
printf '%s\n' "Flash: ./scripts/flash.sh /dev/ttyACM0"
printf '%s\n' "Preview themes: python tools/theme_tool.py preview"
