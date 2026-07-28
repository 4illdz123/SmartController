# utils/sounds.py
import os
import urllib.request
import threading

SOUNDS_DIR = "assets/sounds"

SOUND_URLS = {
    "click": "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3",
    "start": "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3",
    "toggle": "https://assets.mixkit.co/active_storage/sfx/2570/2570-preview.mp3",
}

def ensure_sounds():
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    for name, url in SOUND_URLS.items():
        path = os.path.join(SOUNDS_DIR, f"{name}.mp3")
        if not os.path.exists(path):
            try:
                urllib.request.urlretrieve(url, path)
                print(f"[Sounds] تم تحميل: {name}")
            except Exception as e:
                print(f"[Sounds] فشل تحميل {name}: {e}")

def play(name: str):
    path = os.path.join(SOUNDS_DIR, f"{name}.mp3")
    if not os.path.exists(path):
        return
    def _play():
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception:
            pass
    threading.Thread(target=_play, daemon=True).start()