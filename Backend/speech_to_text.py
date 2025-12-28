import os
import time
import speech_recognition as sr
from langdetect import detect, LangDetectException
import datetime

# Your central TTS
from text_to_speech import TextToSpeech, set_tts_language

# === Configuration ===
QUERY_FILE = "Data/query.txt"
LOG_FILE = "Data/conversation_log.txt"
os.makedirs("Data", exist_ok=True)


# === Save conversation to log ===
def log_conversation(user_input: str, yuna_response: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] 👤 User: {user_input}\n")
        file.write(f"[{timestamp}] 🤖 Tron: {yuna_response}\n\n")


# === Smart multi-language response ===
def build_smart_response(user_input: str, lang_code: str) -> str:
    today = datetime.datetime.now().strftime("%B %d, %Y")

    user_lower = user_input.lower().strip()

    # Special commands
    if "who am i" in user_lower or "mera naam" in user_lower or "నా పేరు" in user_lower:
        if lang_code == "hi":
            return "आप User हैं सर! टोनी स्टार्क वाले — दुनिया के सबसे ब्रिलियंट इंजीनियर। 😎"
        elif lang_code == "te":
            return "మీరు User సార్! టోనీ స్టార్క్ లాంటి — ప్రపంచంలోనే అత్యంత తెలివైన ఇంజనీర్. 😎"
        elif lang_code == "ta":
            return "நீங்கள் User ஐயா! டோனி ஸ்டார்க் போல — உலகின் மிக புத்திசாலி இன்ஜினியர். 😎"
        else:
            return "You are User, sir! The one and only Tony Stark-level genius engineer. 😎"

    elif "today's date" in user_lower or "aaj ki date" in user_lower or "ఈ రోజు తేదీ" in user_lower:
        if lang_code == "hi":
            return f"आज की तारीख है {today} सर।"
        elif lang_code == "te":
            return f"ఈ రోజు తేదీ {today} సార్."
        elif lang_code == "ta":
            return f"இன்றைய தேதி {today} ஐயா."
        else:
            return f"Today's date is {today}, sir."

    elif "clear log" in user_lower or "log delete" in user_lower:
        open(LOG_FILE, 'w').close()
        if lang_code in ["hi", "te", "ta"]:
            return "लॉग क्लियर कर दिया गया सर।"
        return "Conversation log cleared, sir."

    # Default echo + smart reply
    if lang_code == "hi":
        return f"आपने कहा: \"{user_input}\"\nसुन लिया सर, मैं प्रोसेस कर रही हूँ। 🚀"
    elif lang_code == "te":
        return f"మీరు అన్నారు: \"{user_input}\"\nవిన్నాను సార్, ప్రాసెస్ చేస్తున్నాను। 🚀"
    elif lang_code == "ta":
        return f"நீங்கள் சொன்னது: \"{user_input}\"\nகேட்டேன் ஐயா, ப்ராசஸ் செய்கிறேன்। 🚀"
    else:
        return f"You said: \"{user_input}\"\nCopy that, sir. Processing. 🚀"


# === Handle input (text or voice) ===
async def handle_input(user_input: str):
    try:
        # Save query for other modules
        with open(QUERY_FILE, "w", encoding="utf-8") as f:
            f.write(user_input)

        # Detect language
        try:
            detected = detect(user_input)
        except:
            detected = "en"

        # Map to your TTS codes
        if detected.startswith("hi"):
            lang_code = "hi"
            set_tts_language("hi")
        elif detected.startswith("te"):
            lang_code = "te"
            set_tts_language("te")
        elif detected.startswith("ta"):
            lang_code = "ta"
            set_tts_language("ta")
        else:
            lang_code = "en"
            set_tts_language("en")

        # Build smart response
        response = build_smart_response(user_input, lang_code)

        print(f"🤖 Tron: {response}")
        TextToSpeech(response, lang=lang_code)

        # Log
        log_conversation(user_input, response)

    except Exception as e:
        error_msg = "Sorry sir, kuch technical issue aa gaya. Main fix kar dungi."
        print(f"[⚠️] Error: {e}")
        TextToSpeech(error_msg, lang="hi")
        log_conversation(user_input, "[ERROR] " + str(e))


# === Voice Input Loop ===
async def voice_input_loop():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    welcome = "Voice mode activated, sir. Awaiting your command."
    print(f"🎧 [Tron]: {welcome}")
    TextToSpeech(welcome, lang="en")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        try:
            with mic as source:
                print("🎙️ [Tron]: Listening, User...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)

            print("🧠 [Tron]: Recognizing speech...")
            text = recognizer.recognize_google(audio)
            print(f"📄 You said: {text}")

            low = text.lower().strip()

            # Voice commands
            if low in ["exit", "stop", "band karo", "ముగించు", "நிறுத்து"]:
                goodbye = "Goodbye User! System offline."
                TextToSpeech(goodbye, lang="en")
                print("👋 [Tron]: Session ended.")
                break

            elif low in ["switch", "text mode", "type mode"]:
                switch_msg = "Switching to text input mode, sir."
                TextToSpeech(switch_msg, lang="en")
                print("⌨️ [Tron]: Switching to text...")
                return

            elif "hindi mode" in low:
                set_tts_language("hi")
                TextToSpeech("अब से हिंदी में बात करेंगे सर।", lang="hi")
            elif "telugu mode" in low or "telegu mode" in low:
                set_tts_language("te")
                TextToSpeech("ఇకపై తెలుగులో మాట్లాడతాను సార్.", lang="te")
            elif "tamil mode" in low:
                set_tts_language("ta")
                TextToSpeech("இனி தமிழில் பேசுவேன் ஐயா.", lang="ta")
            elif "english mode" in low:
                set_tts_language("en")
                TextToSpeech("English mode activated, sir.", lang="en")

            else:
                await handle_input(text)

        except sr.WaitTimeoutError:
            print("⏳ [Tron]: No input detected...")
        except sr.UnknownValueError:
            sorry = "Sorry sir, I didn't catch that."
            print("❌ [Tron]: Couldn't understand.")
            TextToSpeech(sorry, lang="en")
        except Exception as e:
            print(f"[⚠️] Voice error: {e}")

        time.sleep(0.5)


# === Main Text + Voice Loop ===
async def yuna_loop():
    today = datetime.datetime.now().strftime("%B %d, %Y")
    welcome = f"System online. Good to see you again, MR. STARK. Today is {today}. How can I assist you?"
    print(f"🤖 [Tron]: {welcome}")
    TextToSpeech(welcome, lang="en")

    while True:
        user_input = input("\n💬 Type your command (or 'voice' / 'exit'): ").strip()

        if not user_input:
            continue

        low = user_input.lower()

        if low in ["exit", "bye", "shutdown"]:
            farewell = "Shutting down. Take care, User. Until next time."
            print(f"👋 [Tron]: {farewell}")
            TextToSpeech(farewell, lang="en")
            break

        elif low == "voice":
            print("🎤 [Tron]: Entering voice command mode...")
            TextToSpeech("Voice mode activated.", lang="en")
            await voice_input_loop()
            # After voice loop ends, back to text
            print("⌨️ [Tron]: Back to text mode.")
            TextToSpeech("Returned to text input.", lang="en")

        elif "hindi mode" in low:
            set_tts_language("hi")
            TextToSpeech("हिंदी मोड ऑन हो गया सर।", lang="hi")
        elif "telugu mode" in low:
            set_tts_language("te")
            TextToSpeech("తెలుగు మోడ్ ఆన్ అయింది సార్.", lang="te")
        elif "tamil mode" in low:
            set_tts_language("ta")
            TextToSpeech("தமிழ் மோட் ஆன் ஆகிவிட்டது ஐயா.", lang="ta")
        elif "english mode" in low:
            set_tts_language("en")
            TextToSpeech("English mode activated.", lang="en")

        else:
            await handle_input(user_input)


# === For use by Main.py (fallback speech recognition) ===
def SpeechRecognition():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        with mic as source:
            print("🎙️ [Tron]: Listening for command...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=12)

        print("🧠 [Tron]: Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"📄 Recognized: {text}")
        return text

    except sr.WaitTimeoutError:
        fallback = input("⏳ Timeout. Please type: ")
        return fallback
    except sr.UnknownValueError:
        fallback = input("❌ Not understood. Please type: ")
        return fallback
    except Exception as e:
        print(f"[❌] Speech error: {e}")
        fallback = input("💬 Type your command: ")
        return fallback


# === Run standalone ===
if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(yuna_loop())
    except KeyboardInterrupt:
        print("\n👋 [Tron]: System terminated by Surya.")






