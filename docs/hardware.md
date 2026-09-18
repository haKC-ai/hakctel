# T-LoRa Pager Hardware Notes

The official LILYGO hardware definition lists an ESP32-S3, 16 MB flash, 8 MB PSRAM, 480 x 222 ST7796 display, MIA-M10Q GNSS, LoRa radio, ST25R3916 NFC, BHI260AP smart sensor, ES8311 audio codec, TCA8418 keyboard, DRV2605 haptics, and a microSD slot.

## Shared buses

The display, SD card, NFC controller, and LoRa radio share SPI resources. hakcTEL must use the existing Meshtastic SPI lock and short transactions. External nRF24 support uses the documented Pager header and must not assume exclusive ownership of the bus.

## nRF24 header

| Function | Pager connection |
| --- | --- |
| CE | ESP32-S3 GPIO43 |
| CS | ESP32-S3 GPIO44 |
| MISO | GPIO33 |
| MOSI | GPIO34 |
| SCK | GPIO35 |
| PA direction | XL9555 GPIO9 |

The default nRF24 tool is receive-only. Transmit modes must be opt-in and display channel and power before starting.

## Smart sensor

The BHI260AP combines a six-axis IMU with a programmable sensor processor. It is appropriate for wake gestures, orientation, motion classification, and low-power context events. It is not a general LLM or vision accelerator.
