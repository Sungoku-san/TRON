import threading
import time
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import cv2

# ===============================
# CORE MODULES
# ===============================
from voice_module import TronAssistant
from Tron_Chatbot import ChatBot
from Reminder import Reminder
from conversation_db import log_message, get_conversation_history, clear_history
from text_to_speech import TextToSpeech  # ← gTTS + pyttsx3 fallback chain
from hand_mouse_cursor import HandMouseCursor
from perception_engine import PerceptionEngine
from object_detector import ObjectDetector
from auth import TronAuth

# ===============================
# CONFIG
# ===============================
API_HOST = "127.0.0.1"
API_PORT = 8000
FRONTEND_URL = "http://localhost:3000"

# ===============================
# GLOBAL STATE
# ===============================
tron = TronAssistant()
tts = TextToSpeech()  # ← Reliable gTTS with fallbacks
reminder = Reminder()

# Vision modules
hand_mouse = perception = object_detector = None
hand_thread = perception_thread = detector_thread = None

# ===============================
# AUTHENTICATION
# ===============================
def authenticate():
    auth = TronAuth(tts)
    return auth.authenticate()

# ===============================
# COMMAND HANDLER
# ===============================
def handle_command(command: str) -> str:
    try:
        command = command.strip()
        if not command:
            return "Please say something."

        log_message("user", command, tron.current_lang)

        # Language switch
        lang_result = tron.switch_language(command)
        if lang_result[0]:
            new_lang, confirm = lang_result
            tts.set_language(new_lang)
            log_message("tron", confirm, new_lang)
            tts.speak(confirm)
            return confirm

        # Special commands
        if "clear history" in command.lower():
            clear_history()
            reply = "Conversation history cleared."
            log_message("tron", reply, tron.current_lang)
            tts.speak(reply)
            return reply

        if "show history" in command.lower():
            history = get_conversation_history(10)
            reply = "Recent conversation:\n" + "\n".join(
                f"{h['speaker'].title()}: {h['message']}" for h in history[-10:]
            ) if history else "No history yet."
            log_message("tron", reply, tron.current_lang)
            tts.speak("Check console for recent history.")
            return reply

        if command.lower().startswith("remind me"):
            success, msg = reminder.set_reminder(command)
            log_message("tron", msg, tron.current_lang)
            tts.speak(msg)
            return msg

        if any(p in command.lower() for p in ["exit", "bye", "shutdown"]):
            reply = "Goodbye disabled in web mode."
            tts.speak(reply)
            return reply

        # Chatbot response
        response = ChatBot(command)
        log_message("tron", response, tron.current_lang)
        return response

    except Exception as e:
        traceback.print_exc()
        error = "TRON encountered an error."
        log_message("tron", error, tron.current_lang)
        return error

# ===============================
# VISION THREADS
# ===============================
def run_hand_mouse():
    global hand_mouse
    try:
        hand_mouse = HandMouseCursor()
        tts.speak("Hand gesture control activated.")
        while True:
            frame = hand_mouse.tick()
            if frame is None: break
            cv2.imshow("TRON Hand Mouse", frame)
            if cv2.waitKey(1) == ord('q'): break
    finally:
        if hand_mouse: hand_mouse.release()
        cv2.destroyAllWindows()

def run_perception():
    global perception
    try:
        perception = PerceptionEngine()
        tts.speak("Vision perception online.")
        while True:
            obj, emotion, frame = perception.tick()
            if frame is None: break
            if obj:
                tts.speak(f"I see a {obj}")
            if emotion:
                emo, _ = emotion
                tts.speak(f"You seem {emo}")
            cv2.imshow("TRON Perception", frame)
            if cv2.waitKey(1) == ord('q'): break
    finally:
        if perception: perception.release()

def run_object_detector():
    global object_detector
    try:
        object_detector = ObjectDetector()
        tts.speak("Object detection ready.")
        while True:
            obj, frame = object_detector.detect()
            if frame is None: break
            if obj:
                tts.speak(f"Detected {obj}")
            cv2.imshow("TRON Objects", frame)
            if cv2.waitKey(1) == ord('q'): break
    finally:
        if object_detector: object_detector.release()

# ===============================
# FASTAPI
# ===============================
app = FastAPI(title="TRON v8.0 - gTTS + Fallback", version="8.0")

app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_URL], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    message: str

@app.get("/")
def root():
    return {
        "status": "TRON v8.0 Online",
        "voice": "gTTS (Google) with pyttsx3 offline fallback",
        "say": "Hold mic to talk — I always speak back!"
    }

@app.post("/tron")
def tron_api(data: Query):
    reply = handle_command(data.message)
    tts.speak(reply)
    return {"reply": reply}

@app.post("/speak")
def speak_api(data: Query):
    if data.message.strip():
        tts.speak(data.message)
    return {"status": "speaking"}

# ===============================
# START
# ===============================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🤖 TRON v8.0 — BULLETPROOF VOICE SYSTEM")
    print("   Primary: gTTS (Google)")
    print("   Fallback: pyttsx3 (offline)")
    print("   Last resort: Beep")
    print("   TRON will NEVER be silent!")
    print("="*80 + "\n")

    if not authenticate():
        print("Authentication failed.")
        exit()

    tts.speak("TRON online. Voice system fully operational with fallbacks.")

    # Start vision modules
    threading.Thread(target=run_hand_mouse, daemon=True).start()
    threading.Thread(target=run_perception, daemon=True).start()
    threading.Thread(target=run_object_detector, daemon=True).start()

    try:
        uvicorn.run(app, host=API_HOST, port=API_PORT)
    except KeyboardInterrupt:
        tts.speak("Shutting down. Goodbye.")
        time.sleep(2)
        print("\nTRON offline.")
