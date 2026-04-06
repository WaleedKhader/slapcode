"""SlapCode — gesture-triggered VS Code approval tool for Claude Code."""

import sys
import time
import cv2

from gesture_detector import GestureDetector
from vscode_clicker import click_yes
from sound_player import play_slap


WINDOW_NAME = "SlapCode"

# How long to show the status banner (seconds)
STATUS_DISPLAY_TIME = 1.5


def main():
    detector = GestureDetector()
    if not detector.start():
        print("Failed to open camera. Exiting.")
        sys.exit(1)

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 320, 240)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

    print("SlapCode is running — swipe your hand to approve!")
    print("Press 'q' or close the window to exit.\n")

    status_text = ""
    status_color = (0, 255, 0)
    status_time = 0.0

    try:
        while True:
            frame = detector.read_frame()
            if frame is None:
                break

            triggered = detector.detect(frame)

            if triggered:
                print("[slap detected!]")
                play_slap()
                result = click_yes()
                if result:
                    print("[approved]\n")
                    status_text = "DO IT, NOW!"
                    status_color = (0, 255, 0)
                else:
                    print("[no dialog found]\n")
                    status_text = "NOBODY HOME"
                    status_color = (0, 100, 255)
                status_time = time.time()

            h, w = frame.shape[:2]
            now = time.time()

            # --- Status banner (top center) ---
            if status_text and (now - status_time) < STATUS_DISPLAY_TIME:
                # Semi-transparent overlay bar
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, 50), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

                text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
                tx = (w - text_size[0]) // 2
                cv2.putText(frame, status_text, (tx, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)

            # --- Motion bar (bottom) ---
            ratio = detector.last_motion_ratio
            threshold = detector.motion_area_ratio
            bar_max = threshold * 3
            bar_width = int(min(ratio / max(bar_max, 0.01), 1.0) * (w - 20))
            thresh_x = int((threshold / max(bar_max, 0.01)) * (w - 20)) + 10

            cv2.rectangle(frame, (10, h - 30), (w - 10, h - 10), (50, 50, 50), -1)
            bar_color = (0, 255, 0) if triggered else (200, 150, 0)
            cv2.rectangle(frame, (10, h - 30), (10 + bar_width, h - 10), bar_color, -1)
            cv2.line(frame, (thresh_x, h - 32), (thresh_x, h - 8), (0, 0, 255), 2)

            # --- Idle label ---
            if not status_text or (now - status_time) >= STATUS_DISPLAY_TIME:
                cv2.putText(frame, "Waiting...", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
            else:
                cv2.putText(frame, "SlapCode", (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # --- Motion number ---
            cv2.putText(frame, f"{ratio:.3f}", (10, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        detector.stop()
        cv2.destroyAllWindows()
        print("SlapCode exited.")


if __name__ == "__main__":
    main()
