"""Camera loop + slap gesture detection using optical flow."""

import time
import cv2
import numpy as np


class GestureDetector:
    """Detects a fast lateral hand-swipe (slap) gesture via webcam."""

    def __init__(self, camera_index=0, cooldown=1.0, flow_threshold=6.0, motion_area_ratio=0.06):
        self.camera_index = camera_index
        self.cooldown = cooldown
        self.flow_threshold = flow_threshold
        self.motion_area_ratio = motion_area_ratio

        self._cap = None
        self._prev_gray = None
        self._last_trigger_time = 0.0
        self.last_motion_ratio = 0.0  # exposed for debug overlay

    def start(self):
        """Open the camera. Returns True on success."""
        self._cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self._cap.set(cv2.CAP_PROP_FPS, 30)
        if not self._cap.isOpened():
            print("[gesture] cannot open camera")
            return False
        # warm-up
        for _ in range(5):
            self._cap.read()
        return True

    def read_frame(self):
        """Read a single BGR frame. Returns None if camera is closed."""
        if self._cap is None or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        return frame if ret else None

    def detect(self, frame):
        """Analyse *frame* for a slap gesture. Returns True if triggered."""
        small = cv2.resize(frame, (160, 120))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if self._prev_gray is None:
            self._prev_gray = gray
            self.last_motion_ratio = 0.0
            return False

        # Dense optical flow (Farneback)
        flow = cv2.calcOpticalFlowFarneback(
            self._prev_gray, gray, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0,
        )
        self._prev_gray = gray

        # Use total motion magnitude (not just horizontal)
        mag = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        strong = mag > self.flow_threshold
        ratio = np.count_nonzero(strong) / strong.size
        self.last_motion_ratio = ratio

        now = time.time()
        if ratio >= self.motion_area_ratio and (now - self._last_trigger_time) > self.cooldown:
            self._last_trigger_time = now
            return True
        return False

    def stop(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None
