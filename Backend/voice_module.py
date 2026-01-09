import os
import asyncio
import pygame
import logging
import edge_tts
from langdetect import detect, LangDetectException
import speech_recognition as sr
from io import BytesIO

# Initialize pygame mixer for playback
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Global current language
CURRENT_LANG = "en"

# Edge-TTS: High-quality natural voices
LANG_VOICES = {
    "en": "en-US-AriaNeural",
    "hi": "hi-IN-SwaraNeural",
    "te": "te-IN-ShrutiNeural",
    "ta": "ta-IN-PallaviNeural",
}

# Speech Recognition language codes (Google)
LANG_CODES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "te": "te-IN",
    "ta": "ta-IN"
}

FALLBACK_VOICE = "en-US-AriaNeural"
SPEECH_FILE = os.path.join("Data", "speech.mp3")
os.makedirs("Data", exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Speech Recognizer
recognizer = sr.Recognizer()

# ======================
# TEXT-TO-SPEECH
# ======================

async def _tts_play(text: str, voice: str):
    try:
        if os.path.exists(SPEECH_FILE):
            os.remove(SPEECH_FILE)

        communicate = edge_tts.Communicate(text, voice, rate="+12%")
        await communicate.save(SPEECH_FILE)

        if os.path.getsize(SPEECH_FILE) > 2000:
            pygame.mixer.music.load(SPEECH_FILE)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(30)
    except Exception as e:
        logger.error(f"TTS Error: {e}")

def TextToSpeech(text: str, force_lang: str = None):
    global CURRENT_LANG
    if not text or not text.strip():
        return

    text = text.strip()

    # Detect language
    if force_lang and force_lang.lower() in LANG_VOICES:
        CURRENT_LANG = force_lang.lower()
    else:
        try:
            detected = detect(text)
            if detected.startswith("hi"):
                CURRENT_LANG = "hi"
            elif detected.startswith("te"):
                CURRENT_LANG = "te"
            elif detected.startswith("ta"):
                CURRENT_LANG = "ta"
            else:
                CURRENT_LANG = "en"
        except:
            CURRENT_LANG = "en"

    voice = LANG_VOICES.get(CURRENT_LANG, FALLBACK_VOICE)

    # Chunk long text
    chunks = [text[i:i+350] for i in range(0, len(text), 350)]
    for i, chunk in enumerate(chunks):
        asyncio.run(_tts_play(chunk, voice))
        if i < len(chunks) - 1:
            pygame.time.wait(800)

def set_tts_language(lang: str):
    global CURRENT_LANG
    lang = lang.lower()
    if lang in ["en", "english"]:
        CURRENT_LANG = "en"
    elif lang in ["hi", "hindi"]:
        CURRENT_LANG = "hi"
    elif lang in ["te", "telugu"]:
        CURRENT_LANG = "te"
    elif lang in ["ta", "tamil"]:
        CURRENT_LANG = "ta"
    logger.info(f"Language set to: {CURRENT_LANG.upper()}")

# ======================
# SPEECH-TO-TEXT
# ======================

def SpeechRecognition(audio_stream=None, timeout=6):
    """Recognize speech from mic or audio bytes"""
    global CURRENT_LANG
    lang_code = LANG_CODES.get(CURRENT_LANG, "en-IN")

    with (sr.Microphone() if audio_stream is None else sr.AudioFile(audio_stream)) as source:
        if audio_stream is not None:
            audio_stream.seek(0)
        if audio_stream is None:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            logger.info(f"Listening... ({CURRENT_LANG.upper()})")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            text = recognizer.recognize_google(audio, language=lang_code)
            logger.info(f"Recognized: {text}")
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            logger.error(f"STT Error: {e}")
            return ""

# Export

__all__ = ["TextToSpeech", "SpeechRecognition", "set_tts_language", "CURRENT_LANG"]
