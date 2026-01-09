# text_to_speech.py
# Ultimate reliable TTS: gTTS + pygame with safe file handling

import threading
import tempfile
import os
import time
from gtts import gTTS
import pygame

class TextToSpeech:
    def __init__(self):
        self.lang_map = {
            "en": "en",
            "hi": "hi",
            "te": "te",
            "ta": "ta"
        }
        self.current_lang = "en"

        # Initialize pygame mixer safely
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("🎙️ pygame initialized for reliable playback")
        except Exception as e:
            print(f"pygame init failed: {e}")

        print("🎙️ gTTS ready — Reliable Google voices with safe playback!")

    def set_language(self, lang: str):
        if lang in self.lang_map:
            self.current_lang = lang
            print(f"TTS Language → {lang.upper()}")

    def speak(self, text: str):
        if not text or not text.strip():
            return

        print(f"[TRON SPEAKING ({self.current_lang.upper()})]: {text}")

        def _play():
            mp3_path = None
            try:
                tts_obj = gTTS(text=text, lang=self.lang_map.get(self.current_lang, "en"), slow=False)

                # Use unique temp file
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                mp3_path = tmp_file.name
                tmp_file.close()

                tts_obj.save(mp3_path)

                # Play and wait
                pygame.mixer.music.load(mp3_path)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

            except Exception as e:
                print(f"gTTS error: {e}")
            finally:
                # Safe cleanup after playback
                if mp3_path and os.path.exists(mp3_path):
                    try:
                        # Wait a moment before deleting
                        time.sleep(0.2)
                        os.unlink(mp3_path)
                    except Exception as e:
                        print(f"Cleanup error: {e}")

        threading.Thread(target=_play, daemon=True).start()