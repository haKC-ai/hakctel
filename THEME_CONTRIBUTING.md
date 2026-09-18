# Contributing hakcTEL Themes

Themes are data packs. A theme may change colors, labels, layout hints, dot-matrix treatment, haptic choices, and RTTTL sounds. A theme may not contain executable code, scripts, firmware binaries, credentials, tracking pixels, or remote includes.

## Required files

```text
themes/<theme-id>/
  theme.ini
  preview.svg
```

`theme-id` must contain only lowercase ASCII letters, digits, and hyphens. Keep it under 32 characters.

## Required theme.ini fields

```ini
schema=1
id=example-theme
name=Example Theme
author=Your Name
license=CC0-1.0
description=One short sentence.
colors.header_bg=#1A1A1A
colors.header_text=#FFFFFF
colors.header_status=#73F2A7
colors.body_bg=#050505
colors.body_fg=#D8FFE6
colors.accent=#73F2A7
colors.muted=#62726A
colors.good=#73F2A7
colors.warn=#FFC857
colors.bad=#FF5C5C
full_frame_invert=false
sound.boot=boot:d=16,o=5,b=180:c6,g6
sound.message=msg:d=16,o=6,b=220:c,e,g
sound.sent=sent:d=32,o=6,b=240:g,c7
sound.error=err:d=16,o=4,b=120:g,p,g
```

The parser rejects unknown schema versions, invalid colors, oversized fields, path traversal, and RTTTL strings longer than 230 bytes.

## Visual requirements

- Design for 480 x 222 pixels in landscape orientation.
- Body text must meet a 4.5:1 contrast ratio.
- Large status text and icons must meet 3:1.
- Do not rely on color alone for talk, receive, warning, or error state.
- Keep the center 420 x 178 pixels usable. The rest may be cropped by display offsets.
- Use original artwork. Historical products may inspire color and geometry, but do not copy logos, bitmaps, fonts, or proprietary sounds.

## Sound requirements

- Use RTTTL only in version 1 packs.
- Keep each event under two seconds.
- Message and error sounds must remain distinguishable at low volume.
- Do not transcribe trademarked ringtones note for note. Create an original sound with the same era and function.
- State the sound license in `theme.ini`.

## Test locally

```bash
source .venv-hakctel/bin/activate
python tools/theme_tool.py validate
python tools/theme_tool.py preview
python tools/theme_tool.py catalog --output site/themes/catalog.json
```

Then copy the pack to `/hakctel/themes/<theme-id>/` on the card and put the ID in `/hakctel/active-theme.txt`.

## Pull request checklist

- The validator passes.
- `preview.svg` matches the current pack.
- All text is ASCII.
- The license permits redistribution.
- No executable content is present.
- The theme remains legible in sunlight and at minimum backlight.
- PTT themes show an explicit transmitting indicator.
