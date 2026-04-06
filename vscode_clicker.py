"""Find the VS Code window, locate the '1 Yes' QuickPick item, and click it."""

import time
import ctypes
import cv2
import pyautogui
import pygetwindow as gw
import numpy as np
from PIL import ImageGrab


# Exact HSV range of the QuickPick "1 Yes" highlight (blue-teal selection bar)
# Measured: HSV=(100, 190, 160), RGB=(41, 122, 160)
_HSV_LO = np.array([93, 140, 110])
_HSV_HI = np.array([108, 230, 200])

# A valid highlight row must have this many matching pixels across
_MIN_ROW_PIXELS = 200

# Need at least this many consecutive rows to count as a highlight bar
_MIN_ROW_HEIGHT = 10


def _find_vscode_window():
    """Return the first window whose title contains 'Visual Studio Code'."""
    for w in gw.getWindowsWithTitle("Visual Studio Code"):
        if w.visible and w.width > 100 and w.height > 100:
            return w
    return None


def _bring_to_front(hwnd):
    """Bring a window to the foreground using Win32 API."""
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    SW_RESTORE = 9
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
    current_thread = kernel32.GetCurrentThreadId()
    fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
    if current_thread != fg_thread:
        user32.AttachThreadInput(fg_thread, current_thread, True)
    user32.SetForegroundWindow(hwnd)
    if current_thread != fg_thread:
        user32.AttachThreadInput(fg_thread, current_thread, False)


def _find_highlight_bar(img_rgb):
    """Find the highlighted '1 Yes' bar by scanning for its exact color.

    Returns (center_x, center_y) in image coordinates, or None.
    """
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, _HSV_LO, _HSV_HI)

    # Count matching pixels per row
    row_counts = mask.sum(axis=1) // 255

    # Find consecutive rows with enough matching pixels (the highlight bar)
    bar_start = None
    bar_end = None
    best_start = None
    best_len = 0

    for y in range(len(row_counts)):
        if row_counts[y] >= _MIN_ROW_PIXELS:
            if bar_start is None:
                bar_start = y
            bar_end = y
        else:
            if bar_start is not None:
                length = bar_end - bar_start + 1
                if length > best_len:
                    best_len = length
                    best_start = bar_start
                bar_start = None

    # Check last run
    if bar_start is not None:
        length = bar_end - bar_start + 1
        if length > best_len:
            best_len = length
            best_start = bar_start

    if best_len < _MIN_ROW_HEIGHT:
        return None

    # Get the center of the bar
    cy = best_start + best_len // 2

    # Get horizontal center of matching pixels in the bar rows
    bar_mask = mask[best_start:best_start + best_len, :]
    col_sums = bar_mask.sum(axis=0)
    active_cols = np.where(col_sums > 0)[0]
    if len(active_cols) == 0:
        return None
    cx = int(active_cols.mean())

    return cx, cy


def click_yes():
    """Find and click the '1 Yes' button in the Claude Code approval dialog.

    Returns True if the click was performed, False otherwise.
    """
    win = _find_vscode_window()
    if win is None:
        print("[clicker] VS Code window not found")
        return False

    try:
        _bring_to_front(win._hWnd)
    except Exception as e:
        print(f"[clicker] could not focus VS Code: {e}")
        return False

    time.sleep(0.2)

    left = max(win.left, 0)
    top = max(win.top, 0)
    right = win.left + win.width
    bottom = win.top + win.height

    try:
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
    except Exception as e:
        print(f"[clicker] screenshot failed: {e}")
        return False

    img = np.array(screenshot)
    result = _find_highlight_bar(img)

    if result is None:
        print("[clicker] highlight bar not found — dialog may not be visible")
        return False

    cx, cy = result
    screen_x = left + cx
    screen_y = top + cy

    print(f"[clicker] clicking '1 Yes' at ({screen_x}, {screen_y})")
    pyautogui.click(screen_x, screen_y)
    return True
