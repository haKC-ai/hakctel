# Edge Actions

Edge Actions turns local sensor events into device actions without sending raw sensor data to a server.

## Current sensor path

The Meshtastic BHI260AP driver is included in the `hakctel` build and exposes the sensor firmware's wrist-tilt wake event when that virtual sensor is present. This first Edge Action does not need a machine-learning model.

## Planned deterministic actions

- double tap to open the inbox;
- rotate to silence;
- shake to return home;
- stationary and moving context for power policy.

These will use BHI260AP virtual-sensor outputs and deterministic thresholds as the upstream driver exposes them. They are not presented as completed controls in the current build.

## Optional TinyML

`HAKCTEL_ENABLE_TINYML` reserves an application boundary for small quantized models running on the ESP32-S3. Models live in firmware, not themes. A model manifest must declare input shape, arena size, expected latency, source, license, and SHA-256 digest.

Candidate uses:

- custom gesture classification;
- motion anomaly detection;
- short offline command classification from typed text;
- acoustic event classification after explicit microphone activation.

No always-on microphone model is enabled by default. The UI must show when the microphone is active.
