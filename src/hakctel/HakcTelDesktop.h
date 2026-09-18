#pragma once

#ifdef HAKCTEL_FIRMWARE

#include "Observer.h"
#include "input/InputBroker.h"
#include "mesh/MeshModule.h"

namespace hakctel
{

/**
 * The PageWriter 2000X "timeport-grid" home screen: a 5x2 application grid in a segmented
 * status-bar shell, styled after a late-1990s two-way pager desktop.
 *
 * Registered as a MeshModule UI frame (not a new display stack -- see docs/architecture.md
 * for why) so it slots into the existing Screen.cpp frame carousel for free: the header/nav
 * overlay, frame transitions, and every stock screen (messages, nodes, menus) keep working.
 * It draws only when the active theme sets ui.layout=timeport-grid; every other theme leaves
 * the stock Meshtastic screens untouched.
 */
class HakcTelDesktopModule : public MeshModule, public Observable<const UIFrameEvent *>
{
  public:
    static constexpr uint8_t kCols = 5;
    static constexpr uint8_t kRows = 2;
    static constexpr uint8_t kCellCount = kCols * kRows;

    HakcTelDesktopModule();

    void drawFrame(OLEDDisplay *display, OLEDDisplayUiState *state, int16_t x, int16_t y) override;

  protected:
    // This screen displays state, it never originates or consumes mesh traffic.
    bool wantPacket(const meshtastic_MeshPacket *p) override { return false; }
    bool wantUIFrame() override;
    Observable<const UIFrameEvent *> *getUIFrameObservable() override { return this; }

  private:
    int handleInputEvent(const InputEvent *event);

    CallbackObserver<HakcTelDesktopModule, const InputEvent *> inputObserver =
        CallbackObserver<HakcTelDesktopModule, const InputEvent *>(this, &HakcTelDesktopModule::handleInputEvent);

    uint8_t cursor = 0; // 0..9, row = cursor / kCols, col = cursor % kCols
};

extern HakcTelDesktopModule *hakcTelDesktopModule;

} // namespace hakctel

#endif
