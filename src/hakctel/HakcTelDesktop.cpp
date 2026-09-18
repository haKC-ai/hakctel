#include "configuration.h"

#ifdef HAKCTEL_FIRMWARE

#include "HakcTelDesktop.h"
#include "HakcTelTheme.h"

#include "gps/RTC.h"                     // getTime()
#include "graphics/Screen.h"             // isShowingModuleFrame()
#include "graphics/SharedUIDisplay.h"    // extern bool hasUnreadMessage
#include "graphics/TFTColorRegions.h"    // graphics::isThemeFullFrameInvert()
#include "main.h"                        // extern std::unique_ptr<graphics::Screen> screen

namespace hakctel
{

HakcTelDesktopModule *hakcTelDesktopModule;

namespace
{

// Label + a shape id, not a bitmap: see HakcTelDesktop.h for why these are drawn as vector
// glyphs (drawRect/drawLine/drawCircle) instead of hand-authored XBM art. Order and count
// (5x2) match the PageWriter 2000X spec: mail, compose, delete, alerts, tasks / book, message
// log, sounds, clock, more.
enum class Glyph : uint8_t { Mail, Compose, Delete, Warning, Check, Book, List, Note, Clock, More };

struct Cell {
    Glyph glyph;
    const char *label;
};

constexpr Cell kCells[HakcTelDesktopModule::kCellCount] = {
    {Glyph::Mail, "Inbox"},   {Glyph::Compose, "Compose"}, {Glyph::Delete, "Clear"}, {Glyph::Warning, "Alerts"},
    {Glyph::Check, "Tasks"},  {Glyph::Book, "Nodes"},      {Glyph::List, "Log"},     {Glyph::Note, "Sound"},
    {Glyph::Clock, "Clock"},  {Glyph::More, "More"},
};

// Draws one glyph centered in [x, y, w, h], in the CURRENT display color. Deliberately simple
// line art -- the period-correct pixel font/icon set is tracked as follow-up polish, not
// invented here. See docs/tools.md and the theme-sync doc for the SD-pack precedent this
// screen extends.
void drawGlyph(OLEDDisplay *display, Glyph glyph, int16_t x, int16_t y, int16_t w, int16_t h)
{
    const int16_t cx = x + w / 2;
    const int16_t cy = y + h / 2;
    const int16_t s = (w < h ? w : h) - 6; // glyph bounding box, inset from the cell
    const int16_t left = cx - s / 2;
    const int16_t top = cy - s / 2;

    switch (glyph) {
    case Glyph::Mail:
        display->drawRect(left, top, s, s * 3 / 4);
        display->drawLine(left, top, cx, top + s * 3 / 8);
        display->drawLine(cx, top + s * 3 / 8, left + s, top);
        break;
    case Glyph::Compose:
        display->drawRect(left, top, s * 3 / 4, s);
        display->drawLine(left + s * 3 / 4, top + s, left + s, top);
        break;
    case Glyph::Delete:
        display->drawLine(left, top, left + s, top + s);
        display->drawLine(left, top + s, left + s, top);
        break;
    case Glyph::Warning:
        display->drawTriangle(cx, top, left, top + s, left + s, top + s);
        display->drawVerticalLine(cx, top + s * 3 / 8, s * 3 / 8 - 2);
        display->setPixel(cx, top + s - 3);
        break;
    case Glyph::Check:
        display->drawRect(left, top, s, s);
        display->drawLine(left + 2, top + s / 2, left + s / 2, top + s - 3);
        display->drawLine(left + s / 2, top + s - 3, left + s - 2, top + 2);
        break;
    case Glyph::Book:
        display->drawLine(cx, top, cx, top + s);
        display->drawLine(left, top + 2, cx, top);
        display->drawLine(left, top + 2, left, top + s - 2);
        display->drawLine(left, top + s - 2, cx, top + s);
        display->drawLine(left + s, top + 2, cx, top);
        display->drawLine(left + s, top + 2, left + s, top + s - 2);
        display->drawLine(left + s, top + s - 2, cx, top + s);
        break;
    case Glyph::List:
        for (int16_t row = 0; row < 3; row++)
            display->drawHorizontalLine(left, top + row * (s / 2), s);
        break;
    case Glyph::Note:
        display->drawVerticalLine(left + s - 3, top, s - 4);
        display->drawCircle(left + 3, top + s - 4, 3);
        display->drawCircle(left + s - 6, top + s - 7, 3);
        break;
    case Glyph::Clock:
        display->drawCircle(cx, cy, s / 2);
        display->drawLine(cx, cy, cx, top + 2);
        display->drawLine(cx, cy, cx + s / 4, cy);
        break;
    case Glyph::More:
        display->fillRect(left, cy - 1, 2, 2);
        display->fillRect(cx - 1, cy - 1, 2, 2);
        display->fillRect(left + s - 2, cy - 1, 2, 2);
        break;
    }
}

} // namespace

HakcTelDesktopModule::HakcTelDesktopModule() : MeshModule("hakctelDesktop")
{
    if (inputBroker)
        inputObserver.observe(inputBroker);
}

bool HakcTelDesktopModule::wantUIFrame()
{
    // Only take a frame when the active theme actually asks for the grid layout AND the
    // full-frame invert region it depends on is registered -- see HakcTelDesktop.h and
    // Screen.cpp's prepareFrameColorRegions(). Without the invert region every pixel this
    // screen sets renders the hardcoded default (white), not the theme ink.
    return timeportLayout() && graphics::isThemeFullFrameInvert();
}

void HakcTelDesktopModule::drawFrame(OLEDDisplay *display, OLEDDisplayUiState *state, int16_t x, int16_t y)
{
    const int16_t w = display->getWidth();
    const int16_t h = display->getHeight();
    constexpr int16_t headerH = 22;
    constexpr int16_t footerH = 18;
    const int16_t bodyTop = y + headerH;
    const int16_t bodyH = h - headerH - footerH;
    const int16_t cellW = w / HakcTelDesktopModule::kCols;
    const int16_t cellH = bodyH / HakcTelDesktopModule::kRows;

    display->setColor(WHITE);

    // --- Header: title box + clock box, matching the segmented-box look of the spec. ---
    display->drawRect(x, y, w, headerH);
    const int16_t clockBoxW = 70;
    display->drawVerticalLine(x + w - clockBoxW, y, headerH);
    display->drawString(x + 6, y + 4, "hakcTEL DESKTOP");

    const uint32_t secs = getTime(true);
    const uint32_t hour24 = (secs / 3600) % 24;
    const uint32_t minute = (secs / 60) % 60;
    const uint32_t hour12 = (hour24 % 12 == 0) ? 12 : (hour24 % 12);
    char clockBuf[12];
    snprintf(clockBuf, sizeof(clockBuf), "%2u:%02u %s", hour12, minute, hour24 < 12 ? "AM" : "PM");
    display->drawString(x + w - clockBoxW + 6, y + 4, clockBuf);

    // --- Body: 5x2 icon grid, selected cell drawn inverted (solid box, punched-out glyph). ---
    for (uint8_t i = 0; i < HakcTelDesktopModule::kCellCount; i++) {
        const uint8_t row = i / HakcTelDesktopModule::kCols;
        const uint8_t col = i % HakcTelDesktopModule::kCols;
        const int16_t cx = x + col * cellW;
        const int16_t cy = bodyTop + row * cellH;
        const bool selected = (i == cursor);

        if (selected) {
            display->setColor(WHITE);
            display->fillRect(cx + 2, cy + 2, cellW - 4, cellH - 4);
            display->setColor(BLACK);
        } else {
            display->setColor(WHITE);
            display->drawRect(cx + 2, cy + 2, cellW - 4, cellH - 4);
        }
        drawGlyph(display, kCells[i].glyph, cx, cy, cellW, cellH - 10);
        if (selected)
            display->setColor(WHITE);
    }

    // --- Footer: real unread flag; no outbox queue exists in this tree, say so plainly
    //     rather than print a fabricated zero. ---
    display->setColor(WHITE);
    display->drawHorizontalLine(x, y + h - footerH, w);
    char footerBuf[40];
    snprintf(footerBuf, sizeof(footerBuf), "Unread: %d", graphics::hasUnreadMessage ? 1 : 0);
    display->drawString(x + 4, y + h - footerH + 2, footerBuf);
    display->drawString(x + w - 90, y + h - footerH + 2, "Outbox: --");
}

int HakcTelDesktopModule::handleInputEvent(const InputEvent *event)
{
    if (!screen || !screen->isShowingModuleFrame(this))
        return 0; // Not our frame right now -- let Screen's own nav handle it.

    switch (event->inputEvent) {
    case INPUT_BROKER_UP:
        cursor = (cursor + kCellCount - 1) % kCellCount; // rotary CCW
        break;
    case INPUT_BROKER_DOWN:
        cursor = (cursor + 1) % kCellCount; // rotary CW
        break;
    case INPUT_BROKER_LEFT:
        cursor = (cursor + kCellCount - kCols) % kCellCount; // keyboard: row up
        break;
    case INPUT_BROKER_RIGHT:
        cursor = (cursor + kCols) % kCellCount; // keyboard: row down
        break;
    case INPUT_BROKER_SELECT:
        // Cell activation (open the mapped screen) is deliberately not wired yet -- this
        // stage proves the grid renders and navigates on real hardware first. See
        // docs/tools.md for what each cell is meant to reach.
        break;
    default:
        return 0; // Not ours: BACK and every other key must still reach Screen's own handler.
    }

    UIFrameEvent e;
    e.action = UIFrameEvent::Action::REDRAW_ONLY;
    notifyObservers(&e);
    return 1;
}

} // namespace hakctel

#endif
