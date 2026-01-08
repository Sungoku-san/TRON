import time
import difflib
import speech_recognition as sr
import pyttsx3

# ==================================================
# CONFIG
# ==================================================
WAKE_WORDS = ["hey tron", "hello tron", "tron"]
EXIT_WORDS = ["shutdown tron", "bye tron", "exit tron", "sleep tron"]

LANG_CONFIRM = {
    "en": "Language switched to English.",
    "hi": "अब मैं हिंदी में बोलूंगा।",
    "te": "ఇప్పటి నుంచి నేను తెలుగు మాట్లాడుతాను.",
    "ta": "இனிமேல் நான் தமிழில் பேசுவேன்."
}

VOICE_HINTS = {
    "en": "english",
    "hi": "hindi",
    "te": "telugu",
    "ta": "tamil"
}


# ==================================================
# TRON CORE
# ==================================================
class TronAssistant:
    def __init__(self):
        self.current_lang = "en"
        self.speaking = False

        # TTS
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 180)

        # Speech Recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True

        self.mic = sr.Microphone()

        with self.mic as source:
            print("🎧 Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    # --------------------------------------------------
    # VOICE
    # --------------------------------------------------
    def set_voice(self):
        for voice in self.engine.getProperty("voices"):
            if VOICE_HINTS[self.current_lang] in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def speak(self, text):
        if not text.strip():
            return

        self.speaking = True
        self.set_voice()
        self.engine.say(text)
        self.engine.runAndWait()
        self.speaking = False

    # --------------------------------------------------
    # LISTEN
    # --------------------------------------------------
    def listen(self, timeout=5, phrase_limit=6):
        if self.speaking:
            return ""

        with self.mic as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
                return self.recognizer.recognize_google(audio).lower()
            except:
                return ""

    # --------------------------------------------------
    # WAKE WORD
    # --------------------------------------------------
    def is_wake_word(self, text):
        for w in WAKE_WORDS:
            if w in text:
                return True
            if difflib.SequenceMatcher(None, text, w).ratio() > 0.65:
                return True
        return False

    # --------------------------------------------------
    # LANGUAGE SWITCH
    # --------------------------------------------------
    def switch_language(self, text):
        mapping = {
            "english": "en",
            "hindi": "hi",
            "telugu": "te",
            "tamil": "ta"
        }

        for key, lang in mapping.items():
            if key in text:
                self.current_lang = lang
                return lang
        return None

    # --------------------------------------------------
    # BRAIN (PLUG LLM HERE)
    # --------------------------------------------------
    def tron_reply(self, text):
        return f"You said {text}"

    # --------------------------------------------------
    # LIVE MODE
    # --------------------------------------------------
    def live_talk(self):
        print("🟣 TRON live talk mode active. Say 'Hey Tron'.")

        while True:
            heard = self.listen()

            if self.is_wake_word(heard):
                print("🟢 TRON ACTIVATED")
                self.speak("Tron activated. I am listening.")

                while True:
                    command = self.listen(timeout=7, phrase_limit=10)

                    if not command:
                        continue

                    print(f"👤 {command}")

                    if any(exit_word in command for exit_word in EXIT_WORDS):
                        self.speak("Going offline.")
                        return

                    lang = self.switch_language(command)
                    if lang:
                        self.speak(LANG_CONFIRM[lang])
                        continue

                    response = self.tron_reply(command)
                    self.speak(response)


# ==================================================
# START
# ==================================================
if __name__ == "__main__":
    tron = TronAssistant()
    tron.live_talk()
