#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
remote_url="${1:-https://github.com/haKC-ai/hakctel.git}"
cd "$repo_dir"

if [[ -d .git ]]; then
  printf '%s\n' "A Git repository already exists. No changes made." >&2
  exit 1
fi

git init -b main
git remote add origin "$remote_url"

# Source archives ship protobufs/ and meshtestic/ as empty placeholder directories.
# git submodule add refuses an existing non-repo path, so clear them when empty.
for placeholder in protobufs meshtestic; do
  if [[ -d "$placeholder" && -z "$(ls -A "$placeholder")" ]]; then
    rmdir "$placeholder"
  fi
done

git submodule add https://github.com/meshtastic/protobufs.git protobufs
git -C protobufs checkout a5ecf6446cd2915cd630e44b2c75df87c3ae56bb
git submodule add https://github.com/meshtastic/meshTestic meshtestic
git -C meshtestic checkout dcac7e5673005f4d8a2b1f0f6e06877b689d7519
git add .

printf '%s\n' "Repository initialized and staged. Review with: git status"
printf '%s\n' "Then commit and push: git commit -m 'Initial hakcTEL firmware' && git push -u origin main"
