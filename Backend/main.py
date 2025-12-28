import os
import datetime
import base64
from io import BytesIO
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import sys

# === Import your modules ===
from Tron_Chatbot import ChatBot
from text_to_speech import TextToSpeech, set_tts_language
from speech_to_text import SpeechRecognition

# === Load env ===
env = dotenv_values(".env")
USERNAME = env.get("Username", "User")
ASSISTANT_NAME = env.get("Assistantname", "Tron")
TTS_LANG = env.get("TTS_LANG", "en")

set_tts_language(TTS_LANG)

# === FastAPI app (added without changing original logic) ===
app = FastAPI(
    title="TRON v2 API",
    description="TRON backend - Pure TRON ChatBot (No external fallbacks)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request/Response Models ===
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

# === CLI / Welcome / Goodbye (unchanged) ===
def welcome():
    today = datetime.datetime.now().strftime("%B %d, %Y")
    msg = f"System online. Good to see you again, {USERNAME}. Today is {today}. I am {ASSISTANT_NAME}."
    print(f"🤖 {ASSISTANT_NAME}: {msg}")
    TextToSpeech(msg, lang=TTS_LANG)

def goodbye():
    msg = f"Shutting down. Take care, {USERNAME}. Until next time, sir."
    print(f"🤖 {ASSISTANT_NAME}: {msg}")
    TextToSpeech(msg, lang=TTS_LANG)

# === Core chat processing - TRON ONLY (unchanged) ===
def process_query(user_input: str) -> str:
    if not user_input or user_input.strip() == "":
        return "Please say something, sir."

    lower_input = user_input.lower().strip()
    EXIT_WORDS = ["bye tron", "shutdown tron", "exit tron"]
    EXPLAIN_WORDS = ["explain it tron", "explain tron"]

    if any(word in lower_input for word in EXIT_WORDS):
        goodbye()
        return "Goodbye, sir. Shutting down."

    if any(word in lower_input for word in EXPLAIN_WORDS):
        try:
            response = ChatBot("Explain your previous answer in more detail.")
        except Exception as e:
            print(f"[TRON EXPLAIN ERROR] {e}")
            return "I encountered an issue while trying to explain further."
        return response or "No previous response to explain."

    # === Main TRON response ===
    print(f"[INPUT] User: {user_input}")
    try:
        response = ChatBot(user_input)
        print(f"[TRON RESPONSE] {repr(response)}")
    except Exception as e:
        print(f"[TRON ERROR] {e}")
        return "I'm having trouble processing that right now, sir."

    # If TRON explicitly says "i remain silent", replace with polite message
    if not response or str(response).strip().lower() == "i remain silent":
        return "I prefer not to respond to that, sir."

    # If response is empty for any reason
    if not response or not str(response).strip():
        return "I'm not sure how to answer that."

    return str(response)

# === API Endpoints (new - added without touching original logic) ===
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        reply = process_query(request.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/voice", response_model=ChatResponse)
async def voice(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        audio_stream = BytesIO(audio_bytes)
        spoken_text = SpeechRecognition(audio_stream)
        if not spoken_text or spoken_text.strip() == "":
            return ChatResponse(reply="Sorry, I couldn't understand that.")
        reply = process_query(spoken_text)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice error: {str(e)}")

@app.post("/tts")
async def tts_endpoint(body: dict = Body(...)):
    text = body.get("text", "")
    if not text or text.strip() == "":
        text = "No text provided."
    try:
        audio_bytes = TextToSpeech(text, lang=TTS_LANG, return_bytes=True)
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio_base64": audio_base64}
    except Exception as e:
        print(f"[TTS ERROR] {e}")
        return JSONResponse(content={"audio_base64": ""})

@app.get("/")
def root():
    return {"message": f"TRON v2 API is online! Running pure TRON mode."}

# === CLI Mode (unchanged) ===
def cli_mode():
    welcome()
    while True:
        try:
            user_input = input(f"💬 {USERNAME} > ").strip()
            if not user_input:
                continue
            response = process_query(user_input)
            print(f"🤖 {ASSISTANT_NAME}: {response}")
            TextToSpeech(response, lang=TTS_LANG)
            if "Shutting down" in response:
                break
        except KeyboardInterrupt:
            goodbye()
            break
        except Exception as e:
            print(f"[ERROR] {e}")

# === Run server or CLI (unchanged logic, now supports both) ===
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        cli_mode()
    else:
        print("Starting TRON v2 API server... 🚀 (Pure TRON mode)")
        uvicorn.run(app, host="0.0.0.0", port=8000)