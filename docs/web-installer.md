# Cloudflare Pages Web Installer

The static site in `site/` is designed for `https://hakctel.hakc.ai/`.

## Cloudflare Pages settings

| Setting | Value |
| --- | --- |
| Framework preset | None |
| Build command | `python tools/theme_tool.py catalog --output site/themes/catalog.json` |
| Build output directory | `site` |
| Root directory | `/` |
| Custom domain | `hakctel.hakc.ai` |

The browser installer uses `esp-web-tools` and Web Serial. Chrome and Edge are supported. HTTPS is required.

## Theme Archive app

The same Cloudflare Pages site is a browser theme manager. It can:

- search and preview the hosted catalog;
- download any `theme.ini` pack;
- connect to a mounted microSD card through the File System Access API;
- detect installed packs and the active theme;
- compare installed SHA-256 digests with the catalog;
- install, reinstall, or update verified packs; and
- write `/hakctel/active-theme.txt` when a theme is activated.

Direct SD management requires desktop Chrome or Edge over HTTPS. Other browsers retain catalog browsing and downloads. The browser verifies the entire theme in memory before writing it. Theme files are capped at 8192 bytes and remain data only.

## Release artifacts

The release workflow builds:

- `hakctel-firmware.bin`
- `hakctel-bootloader.bin`
- `hakctel-partitions.bin`
- `hakctel-boot-app0.bin`

The checked-in manifest points to the matching assets on the latest GitHub release. Do not point the stable installer at branch artifacts.

## Cloudflare deployment secrets

The optional workflow expects:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

The token needs Pages deploy permission for the hakcTEL project only.
