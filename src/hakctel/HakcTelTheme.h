#pragma once

#ifdef HAKCTEL_FIRMWARE

namespace hakctel
{

bool loadTheme();
bool playBootSound();
bool pttEnabled();
unsigned int pttMaxSeconds();
bool timeportLayout();
const char *notificationRtttl();

} // namespace hakctel

#endif
