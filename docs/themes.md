# Theme System

The theme engine is intentionally small. It reads one bounded INI file from microSD at boot and turns it into the existing Meshtastic TFT palette. It does not execute pack content.

## Selecting a theme

Write one theme ID to:

```text
/hakctel/active-theme.txt
```

Example:

```text
blackberry-9900
```

The matching pack must exist at `/hakctel/themes/blackberry-9900/theme.ini`.

## Failure behavior

The loader keeps the built-in dark palette when:

- the SD card is absent;
- the active theme file is missing;
- the ID contains invalid characters;
- the theme path escapes the theme directory;
- the schema is unsupported;
- a required color is missing or invalid;
- the file exceeds the parser limits.

## Sound events

Version 1 supports `boot`, `message`, `sent`, and `error` RTTTL strings. The current firmware wires boot and message sounds. Sent and error are reserved in the pack format so the event dispatcher can add them without changing existing themes.

## OTA model

The web catalog and CLI distribute the same data-only packs. A future on-device HTTPS client can consume the catalog without changing the theme format. Until certificate pinning and atomic SD writes are hardware-tested, the default update route is the web catalog or `theme_tool.py` with the card mounted on a computer.
