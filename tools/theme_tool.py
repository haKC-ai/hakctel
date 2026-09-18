#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEMES = ROOT / "themes"
MOCKUPS = ROOT / "docs" / "mockups"
ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,30}[a-z0-9]$")
COLOR_RE = re.compile(r"#[0-9A-Fa-f]{6}$")
REQUIRED = {
    "schema",
    "id",
    "name",
    "author",
    "license",
    "description",
    "colors.header_bg",
    "colors.header_text",
    "colors.header_status",
    "colors.body_bg",
    "colors.body_fg",
    "colors.accent",
    "colors.muted",
    "colors.good",
    "colors.warn",
    "colors.bad",
    "full_frame_invert",
    "sound.boot",
    "sound.message",
    "sound.sent",
    "sound.error",
}
OPTIONAL = {"ui.mode", "ui.dots", "ui.layout", "ptt.talk_key", "ptt.max_seconds"}


def parse_theme(path: Path) -> dict[str, str]:
    if path.stat().st_size > 8192:
        raise ValueError(f"{path}: file exceeds 8192 bytes")
    result: dict[str, str] = {}
    for number, raw in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{number}: expected key=value")
        key, value = (part.strip() for part in line.split("=", 1))
        if key in result:
            raise ValueError(f"{path}:{number}: duplicate key {key}")
        if key not in REQUIRED | OPTIONAL:
            raise ValueError(f"{path}:{number}: unknown key {key}")
        result[key] = value
    missing = sorted(REQUIRED - result.keys())
    if missing:
        raise ValueError(f"{path}: missing {', '.join(missing)}")
    validate_theme(path, result)
    return result


def validate_theme(path: Path, theme: dict[str, str]) -> None:
    theme_id = theme["id"]
    if not ID_RE.fullmatch(theme_id) or path.parent.name != theme_id:
        raise ValueError(f"{path}: invalid or mismatched theme id")
    if theme["schema"] != "1":
        raise ValueError(f"{path}: unsupported schema")
    for key in (key for key in theme if key.startswith("colors.")):
        if not COLOR_RE.fullmatch(theme[key]):
            raise ValueError(f"{path}: invalid color {key}")
    if theme["full_frame_invert"] not in {"true", "false"}:
        raise ValueError(f"{path}: full_frame_invert must be true or false")
    for key in (key for key in theme if key.startswith("sound.")):
        value = theme[key]
        if len(value.encode("ascii")) > 230 or ":d=" not in value:
            raise ValueError(f"{path}: invalid RTTTL value {key}")
    if contrast(theme["colors.body_bg"], theme["colors.body_fg"]) < 4.5:
        raise ValueError(f"{path}: body contrast is below 4.5:1")


def load_themes() -> list[dict[str, str]]:
    packs = [parse_theme(path) for path in sorted(THEMES.glob("*/theme.ini"))]
    if not packs:
        raise ValueError("no themes found")
    ids = [pack["id"] for pack in packs]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate theme ids")
    return packs


def rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))


def luminance(value: str) -> float:
    channels = []
    for channel in rgb(value):
        component = channel / 255
        channels.append(component / 12.92 if component <= 0.04045 else ((component + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def icon(name: str, x: int, y: int, color: str, selected: bool = False) -> str:
    ink = color
    if name == "mail":
        art = f'<rect x="{x+7}" y="{y+8}" width="32" height="24" fill="none" stroke="{ink}" stroke-width="3"/><path d="M{x+8} {y+10} L{x+23} {y+23} L{x+38} {y+10}" fill="none" stroke="{ink}" stroke-width="3"/>'
    elif name == "write":
        art = f'<rect x="{x+10}" y="{y+7}" width="24" height="30" fill="none" stroke="{ink}" stroke-width="3"/><path d="M{x+4} {y+35} L{x+15} {y+24} M{x+6} {y+33} L{x+10} {y+37}" stroke="{ink}" stroke-width="3"/>'
    elif name == "tools":
        art = f'<path d="M{x+8} {y+8} L{x+37} {y+37} M{x+37} {y+8} L{x+8} {y+37}" stroke="{ink}" stroke-width="5"/><circle cx="{x+9}" cy="{y+9}" r="5" fill="none" stroke="{ink}" stroke-width="3"/>'
    elif name == "alert":
        art = f'<path d="M{x+23} {y+5} L{x+41} {y+36} H{x+5} Z" fill="none" stroke="{ink}" stroke-width="3"/><path d="M{x+23} {y+14} V{y+26} M{x+23} {y+31} v1" stroke="{ink}" stroke-width="4"/>'
    elif name == "check":
        art = f'<rect x="{x+7}" y="{y+7}" width="31" height="31" fill="none" stroke="{ink}" stroke-width="3"/><path d="M{x+13} {y+23} L{x+20} {y+31} L{x+34} {y+13}" fill="none" stroke="{ink}" stroke-width="5"/>'
    elif name == "book":
        art = f'<path d="M{x+7} {y+7} Q{x+19} {y+4} {x+23} {y+12} Q{x+27} {y+4} {x+39} {y+7} V{y+36} Q{x+28} {y+32} {x+23} {y+39} Q{x+18} {y+32} {x+7} {y+36} Z" fill="none" stroke="{ink}" stroke-width="3"/>'
    elif name == "music":
        art = f'<path d="M{x+17} {y+10} V{y+31} M{x+17} {y+12} L{x+35} {y+7} V{y+27}" fill="none" stroke="{ink}" stroke-width="4"/><circle cx="{x+11}" cy="{y+33}" r="6" fill="{ink}"/><circle cx="{x+29}" cy="{y+29}" r="6" fill="{ink}"/>'
    elif name == "clock":
        art = f'<circle cx="{x+23}" cy="{y+23}" r="18" fill="none" stroke="{ink}" stroke-width="3"/><path d="M{x+23} {y+11} V{y+23} L{x+33} {y+29}" fill="none" stroke="{ink}" stroke-width="3"/>'
    else:
        art = f'<rect x="{x+7}" y="{y+8}" width="32" height="27" rx="2" fill="none" stroke="{ink}" stroke-width="3"/><path d="M{x+13} {y+15} H{x+33} M{x+13} {y+22} H{x+30} M{x+13} {y+29} H{x+26}" stroke="{ink}" stroke-width="2"/>'
    return f'<g shape-rendering="crispEdges">{art}</g>'


def timeport_svg(theme: dict[str, str], x: int, y: int) -> str:
    bg = theme["colors.body_bg"]
    fg = theme["colors.body_fg"]
    muted = theme["colors.muted"]
    cells = [
        ("mail", 42, 82, True),
        ("write", 115, 82, False),
        ("tools", 188, 82, False),
        ("alert", 261, 82, False),
        ("check", 334, 82, False),
        ("book", 42, 137, False),
        ("note", 115, 137, False),
        ("music", 188, 137, False),
        ("clock", 261, 137, False),
        ("note", 334, 137, False),
    ]
    icons = []
    for name, ix, iy, selected in cells:
        if selected:
            icons.append(f'<rect x="{ix-7}" y="{iy-6}" width="61" height="51" fill="{fg}"/>')
            icons.append(icon(name, ix, iy, bg, True))
        else:
            icons.append(icon(name, ix, iy, fg))
    return f'''<g transform="translate({x} {y})">
<rect width="480" height="222" rx="18" fill="#171918" stroke="#3D403D" stroke-width="3"/>
<rect x="19" y="13" width="442" height="196" fill="{bg}" stroke="#050706" stroke-width="5"/>
<g shape-rendering="crispEdges" fill="none" stroke="{fg}" stroke-width="3">
<rect x="29" y="23" width="53" height="43"/><rect x="82" y="23" width="57" height="43"/><rect x="139" y="23" width="210" height="43"/><rect x="349" y="23" width="101" height="43"/>
<rect x="29" y="72" width="421" height="113"/><line x1="29" y1="190" x2="450" y2="190"/><line x1="29" y1="205" x2="450" y2="205"/>
</g>
<text x="55" y="39" fill="{fg}" text-anchor="middle" font-family="monospace" font-size="10" font-weight="700">LOUD</text>
<path d="M44 49 h5 l7 -7 v20 l-7 -7 h-5 z M60 47 q7 5 0 10" fill="none" stroke="{fg}" stroke-width="2"/>
<text x="110" y="39" fill="{fg}" text-anchor="middle" font-family="monospace" font-size="10" font-weight="700">2-WAY</text>
<path d="M95 53 l8 -8 M103 45 l-2 7 l-6 -1 M123 46 l-8 8 M115 54 l2 -7 l6 1" fill="none" stroke="{fg}" stroke-width="2"/>
<text x="151" y="56" fill="{fg}" font-family="monospace" font-size="30" font-weight="900">Read</text>
<text x="358" y="48" fill="{fg}" font-family="monospace" font-size="21" font-weight="900">12:20</text><text x="429" y="48" fill="{fg}" font-family="monospace" font-size="10" font-weight="900">PM</text>
<text x="365" y="62" fill="{fg}" font-family="monospace" font-size="12" font-weight="900">03/01/00</text>
{''.join(icons)}
<text x="39" y="202" fill="{fg}" font-family="monospace" font-size="13" font-weight="900">Unread: 1</text><text x="265" y="202" fill="{fg}" font-family="monospace" font-size="13" font-weight="900">Outbox: 1</text>
<path d="M386 194 h27 l8 4 l-8 4 h-27 l7 -4 z" fill="{muted}"/><rect x="427" y="195" width="14" height="7" fill="none" stroke="{fg}" stroke-width="2"/><rect x="429" y="197" width="8" height="3" fill="{fg}"/>
<rect x="19" y="13" width="442" height="196" fill="url(#dots)" opacity="0.18"/>
</g>'''


def ptt_svg(theme: dict[str, str], x: int, y: int) -> str:
    bg, fg, accent = theme["colors.body_bg"], theme["colors.body_fg"], theme["colors.accent"]
    return f'''<g transform="translate({x} {y})">
<rect width="480" height="222" rx="18" fill="#171717" stroke="{accent}" stroke-width="3"/><rect x="20" y="16" width="440" height="190" fill="{bg}"/>
<rect x="31" y="27" width="418" height="35" fill="none" stroke="{accent}" stroke-width="3"/><text x="43" y="51" fill="{accent}" font-family="monospace" font-size="21" font-weight="900">DIRECT CONNECT</text><text x="436" y="49" fill="{fg}" text-anchor="end" font-family="monospace" font-size="13">CH 01</text>
<text x="43" y="88" fill="{fg}" font-family="monospace" font-size="13">TALKGROUP</text><text x="43" y="123" fill="{accent}" font-family="monospace" font-size="34" font-weight="900">SECKC OPS</text>
<rect x="31" y="142" width="418" height="51" fill="{accent}"/><text x="240" y="174" fill="{bg}" text-anchor="middle" font-family="monospace" font-size="20" font-weight="900">HOLD SPACE TO TALK</text>
</g>'''


def organizer_svg(theme: dict[str, str], x: int, y: int) -> str:
    bg, fg, accent, muted = (theme[k] for k in ("colors.body_bg", "colors.body_fg", "colors.accent", "colors.muted"))
    labels = ["MESSAGES", "CONTACTS", "NOTES", "CALENDAR", "TOOLS", "FILES"]
    tiles = []
    for i, label in enumerate(labels):
        tx = 39 + (i % 3) * 139
        ty = 78 + (i // 3) * 57
        selected = i == 0
        tiles.append(f'<rect x="{tx}" y="{ty}" width="119" height="45" fill="{accent if selected else "none"}" stroke="{fg}" stroke-width="2"/><text x="{tx+59}" y="{ty+27}" fill="{bg if selected else fg}" text-anchor="middle" font-family="monospace" font-size="11" font-weight="900">{label}</text>')
    return f'''<g transform="translate({x} {y})"><rect width="480" height="222" rx="18" fill="#171918" stroke="{accent}" stroke-width="3"/><rect x="20" y="16" width="440" height="190" fill="{bg}"/>
<rect x="30" y="27" width="420" height="36" fill="{theme['colors.header_bg']}"/><text x="41" y="51" fill="{theme['colors.header_text']}" font-family="monospace" font-size="20" font-weight="900">{html.escape(theme['name']).upper()}</text><text x="438" y="50" fill="{theme['colors.header_status']}" text-anchor="end" font-family="monospace" font-size="12">12:42  87%</text>{''.join(tiles)}
<line x1="30" y1="190" x2="450" y2="190" stroke="{muted}" stroke-width="2"/><text x="39" y="202" fill="{fg}" font-family="monospace" font-size="11">SELECT</text><text x="441" y="202" fill="{fg}" text-anchor="end" font-family="monospace" font-size="11">BACK</text></g>'''


def terminal_svg(theme: dict[str, str], x: int, y: int) -> str:
    bg, fg, accent, muted = (theme[k] for k in ("colors.body_bg", "colors.body_fg", "colors.accent", "colors.muted"))
    return f'''<g transform="translate({x} {y})"><rect width="480" height="222" rx="18" fill="#111312" stroke="{accent}" stroke-width="3"/><rect x="20" y="16" width="440" height="190" fill="{bg}"/><rect x="20" y="16" width="440" height="31" fill="{theme['colors.header_bg']}"/><text x="32" y="37" fill="{theme['colors.header_text']}" font-family="monospace" font-size="15" font-weight="900">HAKCTEL // {html.escape(theme['name']).upper()}</text>
<text x="32" y="72" fill="{muted}" font-family="monospace" font-size="13">MESH LINK 0  RSSI -87  SNR +7.5</text><text x="32" y="101" fill="{fg}" font-family="monospace" font-size="16">[01] K0NSOLE  MEET ON LONGFAST</text><text x="32" y="128" fill="{fg}" font-family="monospace" font-size="16">[02] N0CALL   ACK</text><text x="32" y="164" fill="{accent}" font-family="monospace" font-size="17" font-weight="900">&gt; _</text><line x1="30" y1="181" x2="450" y2="181" stroke="{muted}"/><text x="32" y="198" fill="{muted}" font-family="monospace" font-size="11">F1 REPLY   F2 NODES   F3 TOOLS</text></g>'''


def theme_svg(theme: dict[str, str], x: int = 0, y: int = 0) -> str:
    if theme["id"] == "pagewriter-2000x":
        return timeport_svg(theme, x, y)
    if theme.get("ui.mode") == "ptt":
        return ptt_svg(theme, x, y)
    if theme["id"] in {"blackberry-9900", "hp-jornada", "palm-pilot", "palm-treo"}:
        return organizer_svg(theme, x, y)
    return terminal_svg(theme, x, y)


def legacy_theme_svg(theme: dict[str, str], x: int = 0, y: int = 0) -> str:
    esc = html.escape
    body_bg = theme["colors.body_bg"]
    body_fg = theme["colors.body_fg"]
    accent = theme["colors.accent"]
    muted = theme["colors.muted"]
    dots = "0.55" if theme.get("ui.dots", "false") == "true" else "0"
    ptt = theme.get("ui.mode") == "ptt"
    center = "TALK  GROUP 01" if ptt else "INBOX  3 NEW"
    message = "HOLD SPACE TO TALK" if ptt else "K0NSOLE: meet on LongFast"
    return f'''<g transform="translate({x} {y})">
<rect width="480" height="222" rx="22" fill="#111216" stroke="{accent}" stroke-width="3"/>
<rect x="18" y="16" width="444" height="190" rx="8" fill="{body_bg}"/>
<rect x="18" y="16" width="444" height="34" rx="8" fill="{theme['colors.header_bg']}"/>
<text x="34" y="39" fill="{theme['colors.header_text']}" font-family="monospace" font-size="18" font-weight="700">hakcTEL</text>
<text x="446" y="39" fill="{theme['colors.header_status']}" text-anchor="end" font-family="monospace" font-size="14">MESH 87%</text>
<text x="34" y="80" fill="{accent}" font-family="monospace" font-size="24" font-weight="700">{esc(center)}</text>
<line x1="34" y1="91" x2="446" y2="91" stroke="{muted}"/>
<text x="34" y="121" fill="{body_fg}" font-family="monospace" font-size="17">{esc(message)}</text>
<text x="34" y="151" fill="{muted}" font-family="monospace" font-size="14">12:42  CH 0  SNR +7.5</text>
<rect x="34" y="168" width="128" height="24" rx="3" fill="{accent}"/>
<text x="98" y="185" fill="{body_bg}" text-anchor="middle" font-family="monospace" font-size="13" font-weight="700">{'RELEASE' if ptt else 'OPEN'}</text>
<rect x="174" y="168" width="128" height="24" rx="3" fill="none" stroke="{muted}"/>
<text x="238" y="185" fill="{body_fg}" text-anchor="middle" font-family="monospace" font-size="13">{'CONTACTS' if ptt else 'REPLY'}</text>
<rect x="0" y="0" width="480" height="222" rx="22" fill="url(#dots)" opacity="{dots}"/>
</g>'''


def render_previews(themes: list[dict[str, str]]) -> None:
    MOCKUPS.mkdir(parents=True, exist_ok=True)
    defs = '''<defs><pattern id="dots" width="4" height="4" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.55" fill="#000000"/></pattern></defs>'''
    for theme in themes:
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="222" viewBox="0 0 480 222">{defs}{theme_svg(theme)}</svg>\n'''
        (THEMES / theme["id"] / "preview.svg").write_text(svg, encoding="ascii")
    columns = 2
    gap = 24
    rows = (len(themes) + columns - 1) // columns
    width = columns * 480 + (columns + 1) * gap
    height = rows * 270 + gap
    items = []
    for index, theme in enumerate(themes):
        x = gap + (index % columns) * (480 + gap)
        y = gap + (index // columns) * 270
        items.append(theme_svg(theme, x, y))
        items.append(
            f'<text x="{x}" y="{y + 248}" fill="#E8EDF2" font-family="monospace" font-size="18">{html.escape(theme["name"])}</text>'
        )
    sheet = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#090A0D"/>{defs}{''.join(items)}</svg>\n'''
    (MOCKUPS / "theme-contact-sheet.svg").write_text(sheet, encoding="ascii")


def write_catalog(themes: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    items = []
    for theme in themes:
        source = THEMES / theme["id"] / "theme.ini"
        theme_output = output.parent / theme["id"]
        theme_output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, theme_output / "theme.ini")
        preview = THEMES / theme["id"] / "preview.svg"
        if not preview.exists():
            render_previews(themes)
        shutil.copyfile(preview, theme_output / "preview.svg")
        items.append(
            {
                "id": theme["id"],
                "name": theme["name"],
                "description": theme["description"],
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "theme": f"/themes/{theme['id']}/theme.ini",
                "preview": f"/themes/{theme['id']}/preview.svg",
            }
        )
    output.write_text(json.dumps({"schema": 1, "themes": items}, indent=2) + "\n", encoding="ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and render hakcTEL themes")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("preview")
    catalog = sub.add_parser("catalog")
    catalog.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    themes = load_themes()
    if args.command == "preview":
        render_previews(themes)
    elif args.command == "catalog":
        write_catalog(themes, args.output)
    print(f"{args.command}: {len(themes)} themes OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
