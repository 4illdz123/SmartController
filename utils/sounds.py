# utils/sounds.py

import os
import threading
import urllib.request
import pygame

SOUNDS_DIR = "assets/sounds"

SOUND_URLS = {
    "click": "https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3",
    "start": "https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3",
    "toggle": "https://assets.mixkit.co/active_storage/sfx/2570/2570-preview.mp3",
}

loaded_sounds = {}


def ensure_sounds():
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}

    if not pygame.mixer.get_init():
        pygame.mixer.init()

    for name, url in SOUND_URLS.items():
        path = os.path.join(SOUNDS_DIR, f"{name}.mp3")
        if not os.path.exists(path):
            try:
                # تجاوز حظر HTTP 403 Forbidden
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as resp, open(
                    path, "wb"
                ) as out:
                    out.write(resp.read())
                print(f"[Sounds] تم تحميل: {name}")
            except Exception as e:
                print(f"[Sounds] فشل تحميل {name}: {e}")

        if os.path.exists(path):
            try:
                loaded_sounds[name] = pygame.mixer.Sound(path)
            except Exception:
                pass


def play(name: str):

    def _play():
        if name in loaded_sounds:
            try:
                loaded_sounds[name].play()
            except Exception:
                pass

    threading.Thread(target=_play, daemon=True).start()