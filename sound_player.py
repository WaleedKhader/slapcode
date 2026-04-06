"""Sound effect handler for SlapCode."""

import os
import pygame


_SOUND_FILE = os.path.join(os.path.dirname(__file__), "assets", "slap.mp3")
_initialized = False


def _ensure_init():
    global _initialized
    if not _initialized:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        _initialized = True


def play_slap():
    """Play the slap sound effect. Non-blocking."""
    _ensure_init()
    if not os.path.exists(_SOUND_FILE):
        print("[sound] slap.wav not found – skipping sound")
        return
    try:
        sound = pygame.mixer.Sound(_SOUND_FILE)
        sound.play()
    except Exception as e:
        print(f"[sound] playback error: {e}")
