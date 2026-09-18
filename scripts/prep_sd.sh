#!/usr/bin/env bash
# Prepare a microSD card for hakcTEL before flashing the firmware.
#
# The firmware reads its theme from the card, not from flash. A freshly flashed
# Pager with a bare card logs "no theme on card" and stays on the stock palette,
# so run this once against the mounted card and then flash.
set -euo pipefail

repo_url="https://github.com/haKC-ai/hakctel.git"
assume_yes=0
tmp_clone=""

cleanup() {
  [[ -n "$tmp_clone" && -d "$tmp_clone" ]] && rm -rf "$tmp_clone"
  return 0
}
trap cleanup EXIT

usage() {
  cat >&2 <<'EOF'
Usage: prep_sd.sh [-y] <sd-card-mount-point>

Prepares a microSD card for hakcTEL. It will:

  1. Use this checkout's themes/ directory, or clone haKC-ai/hakctel if the
     script is running on its own.
  2. Create <sd-card>/hakctel/themes/.
  3. Copy all 11 theme packs onto the card.
  4. Leave active-theme.txt alone if you already have one, so your selected
     theme survives. With no file there the firmware boots PageWriter 2000X.

It only ever writes inside <sd-card>/hakctel/. Nothing else on the card is
touched and nothing is deleted.

  -y   do not ask for confirmation

Example:
  ./scripts/prep_sd.sh /media/SDCARD
EOF
  exit 2
}

while getopts ":yh" opt; do
  case "$opt" in
    y) assume_yes=1 ;;
    h) usage ;;
    *) usage ;;
  esac
done
shift $((OPTIND - 1))

[[ $# -eq 1 ]] || usage
sd_root="$1"

if [[ ! -d "$sd_root" ]]; then
  printf 'Not a directory: %s\n' "$sd_root" >&2
  printf 'Mount the card first, then pass its mount point.\n' >&2
  exit 1
fi
if [[ ! -w "$sd_root" ]]; then
  printf 'Not writable: %s\n' "$sd_root" >&2
  printf 'Check that the card is not mounted read-only.\n' >&2
  exit 1
fi

# Prefer the checkout this script lives in; fall back to a clone so the script
# also works when downloaded on its own.
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -d "$repo_dir/themes" ]]; then
  themes_src="$repo_dir/themes"
  source_desc="this checkout ($repo_dir)"
else
  command -v git >/dev/null 2>&1 || { printf 'git is required to fetch the themes.\n' >&2; exit 1; }
  tmp_clone="$(mktemp -d)"
  printf 'No themes/ beside this script, cloning %s\n' "$repo_url" >&2
  git clone --depth 1 --quiet "$repo_url" "$tmp_clone/hakctel"
  themes_src="$tmp_clone/hakctel/themes"
  source_desc="a fresh clone of $repo_url"
fi

theme_count="$(find "$themes_src" -mindepth 2 -maxdepth 2 -name theme.ini | wc -l)"
if [[ "$theme_count" -eq 0 ]]; then
  printf 'No theme packs found in %s\n' "$themes_src" >&2
  exit 1
fi

dest="$sd_root/hakctel"
active="$dest/active-theme.txt"

printf '\n'
printf 'hakcTEL microSD prep\n'
printf '  card        : %s\n' "$sd_root"
printf '  themes from : %s\n' "$source_desc"
printf '  packs       : %s\n' "$theme_count"
printf '  writes to   : %s/themes/\n' "$dest"
if [[ -f "$active" ]]; then
  printf '  active theme: %s (keeping your existing choice)\n' "$(tr -d '\r\n' < "$active")"
else
  printf '  active theme: none set, firmware will boot PageWriter 2000X\n'
fi
printf '\nNothing outside %s/ is touched and nothing is deleted.\n\n' "$dest"

if [[ "$assume_yes" -ne 1 && -t 0 ]]; then
  read -r -p 'Continue? [y/N] ' reply
  [[ "$reply" == [yY] ]] || { printf 'Aborted, card unchanged.\n'; exit 1; }
fi

mkdir -p "$dest/themes"
cp -r "$themes_src/." "$dest/themes/"
sync 2>/dev/null || true

copied="$(find "$dest/themes" -mindepth 2 -maxdepth 2 -name theme.ini | wc -l)"
if [[ "$copied" -ne "$theme_count" ]]; then
  printf 'Copied %s of %s packs -- check the card for space or errors.\n' "$copied" "$theme_count" >&2
  exit 1
fi

printf '\n'
printf 'Copied %s theme packs to %s/themes/\n' "$copied" "$dest"
printf '\n'
printf 'READY TO FLASH.\n'
printf '\n'
printf 'Next:\n'
printf '  1. Eject the card and put it back in the Pager.\n'
printf '  2. Open https://hakctel.hakc.codes in desktop Chrome or Edge.\n'
printf '  3. Connect the Pager by USB and select INSTALL HAKCTEL.\n'
printf '\n'
if [[ ! -f "$active" ]]; then
  printf 'It will boot PageWriter 2000X. To pick another theme:\n'
  printf '  echo tokyo-night > %s\n' "$active"
  printf '\n'
  printf 'Available: %s\n' "$(find "$dest/themes" -mindepth 1 -maxdepth 1 -type d -printf '%f ' | tr ' ' '\n' | sort | tr '\n' ' ')"
  printf '\n'
fi
