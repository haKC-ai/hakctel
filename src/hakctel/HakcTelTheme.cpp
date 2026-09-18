#include "configuration.h"

#ifdef HAKCTEL_FIRMWARE

// main.h must precede AudioThread.h: AudioThread.h includes main.h, whose
// "extern AudioThread *audioThread;" needs the class to already be defined.
#include "main.h"

#include "AudioThread.h"
#include "graphics/TFTColorRegions.h"
#include <SD.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

namespace hakctel
{
namespace
{

constexpr size_t kThemeFileLimit = 8192;
constexpr size_t kThemeIdLimit = 31;
// Out-of-box theme, used when the card carries no /hakctel/active-theme.txt.
constexpr const char *kDefaultThemeId = "pagewriter-2000x";
constexpr size_t kRtttlLimit = 230;

graphics::TFTThemeDef runtimeTheme = {};
char themeName[48] = "hakcTEL SD Theme";
char bootSound[kRtttlLimit + 1] = {};
char messageSound[kRtttlLimit + 1] = {};
bool pttMode = false;
unsigned int pttLimitSeconds = 20;
bool loaded = false;

uint16_t rgb565(const char *value)
{
    if (!value || value[0] != '#' || strlen(value) != 7)
        return 0;
    char *end = nullptr;
    const unsigned long rgb = strtoul(value + 1, &end, 16);
    if (!end || *end != '\0')
        return 0;
    const uint8_t r = (rgb >> 16) & 0xff;
    const uint8_t g = (rgb >> 8) & 0xff;
    const uint8_t b = rgb & 0xff;
    return static_cast<uint16_t>(((r & 0xf8) << 8) | ((g & 0xfc) << 3) | (b >> 3));
}

bool parseColor(const String &value, uint16_t &target)
{
    if (value.length() != 7 || value[0] != '#')
        return false;
    for (size_t i = 1; i < value.length(); i++) {
        if (!isxdigit(static_cast<unsigned char>(value[i])))
            return false;
    }
    target = rgb565(value.c_str());
    return true;
}

bool safeThemeId(const String &id)
{
    if (id.length() < 2 || id.length() > kThemeIdLimit)
        return false;
    for (size_t i = 0; i < id.length(); i++) {
        const char c = id[i];
        if (!(c == '-' || (c >= 'a' && c <= 'z') || isdigit(static_cast<unsigned char>(c))))
            return false;
    }
    return id[0] != '-' && id[id.length() - 1] != '-';
}

void copyValue(char *target, size_t targetSize, const String &value)
{
    const size_t count = value.length() < targetSize - 1 ? value.length() : targetSize - 1;
    memcpy(target, value.c_str(), count);
    target[count] = '\0';
}

struct Palette {
    uint16_t headerBg = 0;
    uint16_t headerText = 0;
    uint16_t headerStatus = 0;
    uint16_t bodyBg = 0;
    uint16_t bodyFg = 0;
    uint16_t accent = 0;
    uint16_t muted = 0;
    uint16_t good = 0;
    uint16_t warn = 0;
    uint16_t bad = 0;
    uint16_t seen = 0;
};

void setRole(graphics::TFTColorRole role, uint16_t on, uint16_t off)
{
    runtimeTheme.roles[static_cast<size_t>(role)] = {on, off};
}

void applyPalette(const Palette &p, bool invert)
{
    runtimeTheme.id = 0x48414b43;
    runtimeTheme.name = themeName;
    runtimeTheme.uniqueIdentifier = 0xffffffff;
    runtimeTheme.fullFrameInvert = invert;
    runtimeTheme.visible = false;
    setRole(graphics::TFTColorRole::HeaderBackground, p.headerBg, p.bodyBg);
    setRole(graphics::TFTColorRole::HeaderTitle, p.headerBg, p.headerText);
    setRole(graphics::TFTColorRole::HeaderStatus, p.headerBg, p.headerStatus);
    setRole(graphics::TFTColorRole::SignalBars, p.good, p.bodyBg);
    setRole(graphics::TFTColorRole::ConnectionIcon, p.accent, p.bodyBg);
    setRole(graphics::TFTColorRole::UtilizationFill, p.good, p.bodyBg);
    setRole(graphics::TFTColorRole::FavoriteNode, p.accent, p.bodyBg);
    setRole(graphics::TFTColorRole::ActionMenuBorder, p.accent, p.bodyBg);
    setRole(graphics::TFTColorRole::ActionMenuBody, p.bodyFg, p.bodyBg);
    setRole(graphics::TFTColorRole::ActionMenuTitle, p.headerBg, p.headerText);
    setRole(graphics::TFTColorRole::FrameMono, p.bodyBg, p.bodyFg);
    setRole(graphics::TFTColorRole::BootSplash, p.accent, p.bodyBg);
    setRole(graphics::TFTColorRole::FavoriteNodeBGHighlight, p.accent, p.bodyBg);
    setRole(graphics::TFTColorRole::NavigationBar, p.headerText, p.headerBg);
    setRole(graphics::TFTColorRole::NavigationArrow, p.accent, p.bodyBg);
    runtimeTheme.batteryFillGood = p.good;
    runtimeTheme.batteryFillMedium = p.warn;
    runtimeTheme.batteryFillBad = p.bad;
}

bool parseTheme(File &file)
{
    Palette palette;
    bool invert = false;
    bool schemaValid = false;
    while (file.available()) {
        String line = file.readStringUntil('\n');
        line.trim();
        if (!line.length() || line[0] == '#')
            continue;
        const int split = line.indexOf('=');
        if (split <= 0)
            return false;
        String key = line.substring(0, split);
        String value = line.substring(split + 1);
        key.trim();
        value.trim();
        if (key == "schema")
            schemaValid = value == "1";
        else if (key == "name")
            copyValue(themeName, sizeof(themeName), value);
        else if (key == "colors.header_bg") {
            if (!parseColor(value, palette.headerBg))
                return false;
            palette.seen |= 1u << 0;
        } else if (key == "colors.header_text") {
            if (!parseColor(value, palette.headerText))
                return false;
            palette.seen |= 1u << 1;
        } else if (key == "colors.header_status") {
            if (!parseColor(value, palette.headerStatus))
                return false;
            palette.seen |= 1u << 2;
        } else if (key == "colors.body_bg") {
            if (!parseColor(value, palette.bodyBg))
                return false;
            palette.seen |= 1u << 3;
        } else if (key == "colors.body_fg") {
            if (!parseColor(value, palette.bodyFg))
                return false;
            palette.seen |= 1u << 4;
        } else if (key == "colors.accent") {
            if (!parseColor(value, palette.accent))
                return false;
            palette.seen |= 1u << 5;
        } else if (key == "colors.muted") {
            if (!parseColor(value, palette.muted))
                return false;
            palette.seen |= 1u << 6;
        } else if (key == "colors.good") {
            if (!parseColor(value, palette.good))
                return false;
            palette.seen |= 1u << 7;
        } else if (key == "colors.warn") {
            if (!parseColor(value, palette.warn))
                return false;
            palette.seen |= 1u << 8;
        } else if (key == "colors.bad") {
            if (!parseColor(value, palette.bad))
                return false;
            palette.seen |= 1u << 9;
        }
        else if (key == "full_frame_invert")
            invert = value == "true";
        else if (key == "sound.boot")
            copyValue(bootSound, sizeof(bootSound), value);
        else if (key == "sound.message")
            copyValue(messageSound, sizeof(messageSound), value);
        else if (key == "ui.mode")
            pttMode = value == "ptt";
        else if (key == "ptt.max_seconds") {
            const long seconds = value.toInt();
            if (seconds >= 5 && seconds <= 60)
                pttLimitSeconds = static_cast<unsigned int>(seconds);
        }
    }
    if (!schemaValid || palette.seen != 0x3ff)
        return false;
    applyPalette(palette, invert);
    return true;
}

} // namespace

bool loadTheme()
{
    String id;
    File selected = SD.open("/hakctel/active-theme.txt", FILE_READ);
    if (selected) {
        if (selected.size() > kThemeIdLimit + 2) {
            selected.close();
            return false;
        }
        id = selected.readStringUntil('\n');
        selected.close();
        id.trim();
    }
    if (id.isEmpty()) {
        id = kDefaultThemeId;
        LOG_INFO("hakcTEL: no active-theme.txt, defaulting to %s", kDefaultThemeId);
    }
    if (!safeThemeId(id)) {
        LOG_WARN("hakcTEL: rejected unsafe theme id");
        return false;
    }

    const String path = "/hakctel/themes/" + id + "/theme.ini";
    File file = SD.open(path, FILE_READ);
    if (!file) {
        LOG_WARN("hakcTEL: no theme on card at %s -- copy the repo themes/ to /hakctel/themes/", path.c_str());
        return false;
    }
    const size_t size = file.size();
    if (size == 0 || size > kThemeFileLimit) {
        file.close();
        LOG_WARN("hakcTEL: theme %s is %u bytes, limit is %u", path.c_str(), (unsigned)size, (unsigned)kThemeFileLimit);
        return false;
    }
    loaded = parseTheme(file);
    file.close();
    if (!loaded) {
        LOG_WARN("hakcTEL: invalid theme: %s", path.c_str());
        return false;
    }
    graphics::setRuntimeTheme(&runtimeTheme);
    LOG_INFO("hakcTEL: loaded SD theme %s", id.c_str());
    return true;
}

bool playBootSound()
{
#ifdef HAS_I2S
    if (loaded && bootSound[0] && audioThread) {
        audioThread->beginRttl(bootSound, strlen(bootSound));
        return true;
    }
#endif
    return false;
}

bool pttEnabled()
{
    return loaded && pttMode;
}

unsigned int pttMaxSeconds()
{
    return pttLimitSeconds;
}

const char *notificationRtttl()
{
    return loaded ? messageSound : "";
}

} // namespace hakctel

#endif
