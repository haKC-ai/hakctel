# GLIDE Integration Boundary

GLIDE targets M5Stack Cardputer hardware and is currently distributed under the PolyForm Noncommercial license. hakcTEL is GPL-based. Copying GLIDE source into this repository would create avoidable hardware and licensing problems.

The supported approach is an optional external port:

1. Keep GLIDE-derived source in a separate repository with its required license and attribution.
2. Implement a Pager hardware adapter for the TCA8418 keyboard, ES8311 codec, and 480 x 222 display.
3. Produce a separately named firmware image.
4. Publish it as an optional web-installer target only when its license permits that distribution.

hakcTEL's built-in Tone Lab will be original code and may reuse only general synthesis ideas, not GLIDE source or assets.
