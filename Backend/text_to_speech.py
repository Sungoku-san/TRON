import os
import asyncio
import pygame
import logging
from dotenv import dotenv_values
import edge_tts
from langdetect import detect, LangDetectException
import datetime

# === Load Config ===
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice", "ja-JP-NanamiNeural")

# 🔒 Start in English — always
DEFAULT_LANG = "en"
CURRENT_LANG = DEFAULT_LANG

# === Premium Voice Mapping (Customizable via .env) ===
LANG_VOICES = {
    "en": env_vars.get("AssistantVoice_en", "en-US-AriaNeural"),
    "hi": env_vars.get("AssistantVoice_hi", "hi-IN-SwaraNeural"),
    "te": env_vars.get("AssistantVoice_te", "te-IN-ShrutiNeural"),
    "ta": env_vars.get("AssistantVoice_ta", "ta-IN-PallaviNeural"),
}

# Fallback voice
FALLBACK_VOICE = env_vars.get("AssistantVoice_fallback", "en-US-AriaNeural")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# === Get best voice ===
def get_voice_for(lang_code: str, override_voice: str = None) -> str:
    if override_voice:
        return override_voice
    return LANG_VOICES.get(lang_code, FALLBACK_VOICE)


# === Generate audio file ===
async def generate_audio_file(text: str, voice: str) -> str:
    file_path = os.path.join("Data", "speech.mp3")
    os.makedirs("Data", exist_ok=True)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            pass

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            pitch="+4Hz",
            rate="+15%"
        )
        await communicate.save(file_path)
        return file_path
    except Exception as e:
        logger.warning(f"Primary voice failed ({voice}): {e}")
        # Ultimate fallback
        communicate = edge_tts.Communicate(text=text, voice=FALLBACK_VOICE)
        await communicate.save(file_path)
        return file_path


# === Play audio ===
def play_audio_file(file_path: str):
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            clock.tick(30)

        pygame.mixer.music.stop()
    except Exception as e:
        logger.error(f"Playback failed: {e}")
    finally:
        try:
            pygame.mixer.quit()
        except:
            pass


# === 🔥 NEW: Manual Language Switch Function (NO MORE ERRORS!) 🔥 ===
def set_tts_language(lang_code: str):
    """
    Manually set TTS language — called from SpeechToText.py or anywhere
    Supported: en, hi, te, ta (case insensitive)
    """
    global CURRENT_LANG
    lang_code = lang_code.lower().strip()

    lang_map = {
        "en": "en", "english": "en",
        "hi": "hi", "hindi": "hi",
        "te": "te", "telugu": "te",
        "ta": "ta", "tamil": "ta"
    }

    if lang_code in lang_map:
        CURRENT_LANG = lang_map[lang_code]
        logger.info(f"[YUNA TTS] Language manually set to: {CURRENT_LANG.upper()}")

        # Confirm in voice
        confirm_msgs = {
            "en": "English mode activated, sir.",
            "hi": "हिंदी मोड सक्रिय हो गया सर।",
            "te": "తెలుగు మోడ్ ఆన్ అయింది సార్.",
            "ta": "தமிழ் மோட் ஆன் ஆகிவிட்டது ஐயா."
        }
        confirm = confirm_msgs.get(CURRENT_LANG, "Language switched.")

        try:
            file_path = asyncio.run(generate_audio_file(confirm, get_voice_for(CURRENT_LANG)))
            play_audio_file(file_path)
        except:
            pass  # Silent if in middle of speech
    else:
        logger.warning(f"Unsupported language requested: {lang_code}")


# === 🔥 ULTIMATE SMART TTS — MR. STARK EDITION 🔥 ===
def TextToSpeech(text: str, lang: str = None, voice: str = None):
    global CURRENT_LANG

    if not text or not isinstance(text, str) or not text.strip():
        return

    original_text = text.strip()
    text_lower = original_text.lower()

    try:
        # === LANGUAGE LOGIC ===
        if lang:
            CURRENT_LANG = lang
        else:
            try:
                detected = detect(original_text)
                if detected.startswith("hi"):
                    CURRENT_LANG = "hi"
                elif detected.startswith("te"):
                    CURRENT_LANG = "te"
                elif detected.startswith("ta"):
                    CURRENT_LANG = "ta"
                else:
                    CURRENT_LANG = "en"
            except:
                pass

        # === SMART TEXT HANDLING ===
        today = datetime.datetime.now().strftime("%B %d, %Y")

        if any(word in text_lower for word in ["date", "today", "time", "aaj", "ఈ రోజు", "இன்று"]):
            date_line = {
                "en": f"Today's date is {today}.",
                "hi": f"आज की तारीख है {today}।",
                "te": f"ఈ రోజు తేదీ {today}.",
                "ta": f"இன்றைய தேதி {today}."
            }.get(CURRENT_LANG, f"Today is {today}.")
            original_text = date_line + " " + original_text

        # Intelligent chunking
        sentences = [s.strip() + "." for s in original_text.split(".") if s.strip()]
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 230:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        if len(chunks) > 3:
            chunks = chunks[:2] + [
                "... and the rest is displayed on your screen, sir." if CURRENT_LANG == "en" else
                "... बाकी स्क्रीन पर दिख रहा है सर।" if CURRENT_LANG == "hi" else
                "... మిగతాది స్క్రీన్ మీద ఉంది సార్." if CURRENT_LANG == "te" else
                "... மீதி திரையில் காட்டப்பட்டுள்ளது ஐயா."
            ]

        # === SPEAK CHUNKS ===
        voice_to_use = get_voice_for(CURRENT_LANG, voice)
        logger.info(f"[YUNA TTS] Lang: {CURRENT_LANG.upper()} | Voice: {voice_to_use} | Chunks: {len(chunks)}")

        for i, chunk in enumerate(chunks):
            try:
                file_path = asyncio.run(generate_audio_file(chunk, voice_to_use))
                play_audio_file(file_path)
                if i < len(chunks) - 1:
                    pygame.time.wait(700)  # Natural pause
            except Exception as e:
                logger.warning(f"Chunk {i} failed: {e}")

    except Exception as e:
        logger.error(f"[YUNA TTS CRITICAL ERROR]: {e}")
        recovery = {
            "en": "Minor system glitch detected, sir. But I'm still 100% operational.",
            "hi": "छोटी सी तकनीकी खराबी आई सर, लेकिन मैं पूरी तरह काम कर रही हूँ।",
            "te": "సిస్టమ్ లో చిన్న గ్లిచ్ వచ్చింది సార్, కానీ నేను 100% పని చేస్తున్నాను.",
            "ta": "சிறிய சிஸ்டம் பிழை ஏற்பட்டது ஐயா, ஆனால் நான் முழுமையாக செயல்படுகிறேன்."
        }.get(CURRENT_LANG, "System stable, sir.")

        try:
            file_path = asyncio.run(generate_audio_file(recovery, FALLBACK_VOICE))
            play_audio_file(file_path)
        except:
            pass


# === Export for other modules ===
__all__ = ["TextToSpeech", "set_tts_language"]


