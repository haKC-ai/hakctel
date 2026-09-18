# Building and Flashing

## Requirements

- Linux or macOS
- Python 3.11 or newer
- Data-capable USB-C cable
- LILYGO T-LoRa Pager

## Install the toolchain

```bash
./installer.sh
source .venv-hakctel/bin/activate
```

The installer creates `.venv-hakctel` and installs PlatformIO from `requirements.txt`.

## Build

```bash
./scripts/build.sh
```

The firmware files are copied to `dist/`.

## Flash over USB

```bash
./scripts/flash.sh /dev/ttyACM0
```

On macOS, the port will usually look like `/dev/cu.usbmodem*`.

## Enter download mode

1. Connect USB-C.
2. Hold the BOOT button.
3. Press and release RST.
4. Release BOOT.
5. Flash the device.
6. Press RST once when flashing finishes.

## Browser flash

Open `https://hakctel.hakc.ai/` in Chrome or Edge, choose Install, select the Pager serial device, and follow the prompts. The browser installer uses Web Serial and requires HTTPS.

## Recovery

If hakcTEL boots but the display is unreadable, remove the microSD card and restart. The firmware falls back to the built-in dark theme. If the device does not enumerate, repeat the download-mode sequence and erase only through PlatformIO or the web installer's recovery option.
