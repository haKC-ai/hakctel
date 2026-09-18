#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

./scripts/build.sh
python tools/theme_tool.py catalog --output site/themes/catalog.json
python tools/theme_tool.py preview

printf '%s\n' "Release assets are ready in dist/ and site/."
