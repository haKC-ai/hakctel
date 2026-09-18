# Tools

## Capability levels

| Level | Meaning |
| --- | --- |
| Built-in | Uses existing Pager hardware and is available without accessories |
| Adapter | Requires a supported external module |
| Experimental | Compiles only with an explicit feature flag |
| Specified | UI and safety contract exist, implementation is not claimed complete |

## Tool matrix

| Tool | Level | Default behavior |
| --- | --- | --- |
| Mesh diagnostics | Built-in | Node, channel, signal, queue, and airtime status |
| Wi-Fi survey | Experimental | Passive SSID, BSSID, channel, and RSSI inventory |
| BLE survey | Experimental | Passive advertisement inventory |
| GPS logger | Built-in | GPX and CSV logging to microSD |
| NFC inspector | Experimental | Read NDEF and supported tag metadata |
| I2C explorer | Built-in | Address and known-device inventory |
| GPIO monitor | Built-in | Read-only until the user unlocks an output pin |
| nRF24 analyzer | Adapter | Receive and channel-energy inspection |
| LoRa spectrum view | Experimental | Receive-only RSSI sampling |
| Edge Actions | Experimental | Gesture macros and optional TinyML |
| Tone Lab | Specified | Original synth engine for keyboard and speaker |
| GLIDE bridge | Specified | Optional separately licensed port boundary |

No tool performs deauthentication, jamming, credential interception, replay, or covert transmission by default.
