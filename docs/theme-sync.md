# Theme Repository Sync

The Cloudflare site publishes the catalog at `https://hakctel.hakc.ai/themes/catalog.json`. Every entry includes its theme URL, preview URL, and SHA-256 digest.

The Theme Archive on that site can connect directly to a mounted microSD card in desktop Chrome or Edge. It marks packs as catalog-only, installed, active, or needing an update. Install and Update verify the catalog digest before writing. Activate also writes the selected ID to `/hakctel/active-theme.txt`.

The first release uses a verified companion sync instead of letting a data pack open arbitrary network connections inside the firmware. With the Pager switched off, mount its FAT32 microSD card and run:

```bash
python tools/theme_sync.py --sd-root /media/SDCARD --theme blackberry-9900
```

The tool requires HTTPS, caps download sizes, checks the catalog digest, writes the pack atomically, and updates `active-theme.txt`. Reinsert the card and reboot the Pager.

The command-line tool remains the automation-friendly path. The browser app keeps activation separate from installation so several packs can be staged without changing the active one.

Direct device-side Wi-Fi sync is intentionally not claimed in this release. It needs a trusted CA bundle, a user confirmation screen, rollback storage, and integration testing on the shared SD and radio bus.
