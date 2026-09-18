# Direct Connect Push-to-Talk

The Nextel Direct Connect theme is paired with a real PTT controller, not a decorative button.

## Controls

- Hold the configured PTT key to request the channel and transmit.
- Release to stop transmitting and return to listen mode.
- The display switches between transmit and receive state.
- The theme supplies original RTTTL start and alert sounds.
- A configurable timeout returns a stuck transmitter to receive.

## Transport

Voice uses Meshtastic's Codec2 audio module. The audio module starts only when the selected regional profile permits audio and the codec path is available. Use an encrypted private channel for voice. The firmware cannot determine whether every participant is authorized, so channel ownership remains the operator's responsibility.

The implementation is intended for the SX1280 2.4 GHz Pager SKU. The normal SX1262 sub-GHz profile does not enable this low-latency audio path.

## Limits

LoRa is not iDEN. Audio is low bitrate, half duplex, range and congestion dependent, and suitable only for short bursts. The controller enforces a transmission time limit. Channel use remains subject to local law and Meshtastic region settings.
