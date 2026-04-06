# SlapCode

**Slap your hand to approve Claude Code commands in VS Code.**

SlapCode is a lightweight Windows desktop app that watches your webcam for a hand-slap gesture and automatically clicks the "1 Yes" approval button in the Claude Code VS Code extension.

## How It Works

1. **Camera** — SlapCode opens your webcam and displays a live preview window (always on top)
2. **Gesture Detection** — Using optical flow analysis, it detects fast lateral hand swipes (a "slap" motion through the air)
3. **VS Code Click** — When a slap is detected, it finds the VS Code window, screenshots it, locates the teal-highlighted "1 Yes" button by color, and clicks it
4. **Sound** — A satisfying slap sound plays on each detection

## Prerequisites

- **Windows 10/11** with a webcam
- **Python 3.10+**
- **VS Code** with the [Claude Code extension](https://marketplace.visualstudio.com/items?itemName=anthropics.claude-code)

## Installation

```bash
git clone https://github.com/WaleedKhader/slapcode.git
cd slapcode
pip install -r requirements.txt
```

## Usage

```bash
python slapcode.py
```

- A small camera preview window will appear (always on top)
- Open VS Code with Claude Code running
- When the approval dialog appears, **swipe your hand** in front of the camera
- SlapCode clicks "1 Yes" for you automatically
- Press **q** or close the preview window to exit

## Gesture Guide

The gesture is a **fast horizontal hand swipe** in front of your webcam — like you're slapping the air sideways. Tips:

- Hold your hand ~30–60 cm from the camera
- Swipe quickly left-to-right or right-to-left across the camera's field of view
- A brisk, confident motion works best — slow waves won't trigger it
- There's a 2-second cooldown between detections to prevent double-triggers

## How the Click Works

SlapCode does **not** use keyboard shortcuts or hardcoded coordinates. Instead:

1. Finds the VS Code window by title
2. Takes a screenshot of that window
3. Scans for the teal/cyan highlight color of the "1 Yes" QuickPick item
4. Computes the center of that color region
5. Clicks that exact point with the mouse

This works across all screen sizes, resolutions, and DPI settings.

## Compatibility

- **Windows only** (uses Win32 APIs for window management)
- Requires a webcam
- Tested with VS Code and the Claude Code extension

## License

MIT

## Acknowledgments

SlapCode is a companion tool for the [Claude Code VS Code extension](https://marketplace.visualstudio.com/items?itemName=anthropics.claude-code) by Anthropic.
