import wave
import tempfile
import subprocess
import threading
from piper.voice import PiperVoice

# ==================================================
# CONFIG
# ==================================================
TTS_MODEL_EN = "models/en_US-amy-medium.onnx"  # Change if you add more languages

LANG_CONFIRM = {
    "en": "Language switched to English.",
    "hi": "Language switched to Hindi. Voice will remain in English style for now.",
}

class TronAssistant:  # ← MUST be TronAssistant to match main.py import
    def __init__(self):
        self.current_lang = "en"
        self.voice = None
        self._load_voice()
        print("🎧 Piper TTS loaded - High-quality offline voice ready!")

    def _load_voice(self):
        try:
            self.voice = PiperVoice.load(TTS_MODEL_EN)
            print(f"✅ Loaded Piper voice: {TTS_MODEL_EN}")
        except Exception as e:
            print(f"❌ Failed to load Piper model: {e}")
            print("   Make sure en_US-amy-medium.onnx and .json are in ./models/")
            self.voice = None

    def speak(self, text: str):
        if not text or not text.strip() or self.voice is None:
            return

        print(f"[TRON SPEAKING]: {text}")

        try:
            # Generate WAV in memory
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wav_path = tmp.name

            with wave.open(wav_path, "wb") as wav_file:
                self.voice.synthesize_wav(text, wav_file)

            # Play audio on Windows (no popup window)
            subprocess.run([
                "powershell", "-c",
                f"(New-Object Media.SoundPlayer '{wav_path}').PlaySync(); Remove-Item '{wav_path}' -Force"
            ], creationflags=subprocess.CREATE_NO_WINDOW)

        except Exception as e:
            print("❌ Speech playback failed:", e)

    def switch_language(self, command: str):
        cmd = command.lower()
        new_lang = None

        if any(word in cmd for word in ["english", "इंग्लिश"]):
            new_lang = "en"
        elif any(word in cmd for word in ["hindi", "हिंदी"]):
            new_lang = "hi"

        if new_lang and new_lang != self.current_lang:
            self.current_lang = new_lang
            confirm = LANG_CONFIRM.get(new_lang, "Language updated.")
            # Speak confirmation in background
            threading.Thread(target=self.speak, args=(confirm,), daemon=True).start()
            return new_lang, confirm

        return None, None

