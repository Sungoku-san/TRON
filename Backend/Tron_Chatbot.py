import os
import json
import datetime
import re
from dotenv import dotenv_values

# ===============================
# LOAD ENV
# ===============================
env = dotenv_values(".env")

Username = env.get("Username", "User")
Assistantname = env.get("Assistantname", "Tron")

GEMINI_API_KEY = env.get("GEMINI_API_KEY")
GROQ_API_KEY = env.get("GROQ_API_KEY")
OPENAI_API_KEY = env.get("OPENAI_API_KEY")
COHERE_API_KEY = env.get("COHERE_API_KEY")

# ===============================
# CLIENT IMPORTS
# ===============================
from google import genai  # New official Google GenAI SDK
from groq import Groq
from openai import OpenAI
import cohere

# ===============================
# INIT CLIENTS
# ===============================
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
cohere_client = cohere.Client(api_key=COHERE_API_KEY)

# ===============================
# SYSTEM PROMPT (CUTOFF ISSUE FIXED!)
# ===============================
SYSTEM_PROMPT = (
    f"You are {Assistantname}, a highly intelligent, friendly and helpful AI assistant. "
    f"You are helping {Username} politely and clearly.\n"
    "IMPORTANT RULES:\n"
    "- Always use the CURRENT DATE AND TIME provided in every prompt.\n"
    "- Your knowledge is continuously updated beyond any training cutoff.\n"
    "- NEVER say your knowledge ends in 2023, 2024, or any past year.\n"
    "- If asked about your cutoff, say: 'My knowledge is up to date as of the current date provided.'\n"
    "- Use conversation history, known facts, and real-time info for accurate replies."
)

# ===============================
# MEMORY PATH
# ===============================
BASE_DIR = r"D:\project\ai assistent\Backend"
MEMORY_FILE = os.path.join(BASE_DIR, "conversation_log.json")


# ===============================
# MEMORY CORE
# ===============================
def LoadMemory():
    if not os.path.exists(MEMORY_FILE):
        return {"facts": {}, "conversations": []}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
    memory.setdefault("facts", {})
    memory.setdefault("conversations", [])
    return memory


def SaveMemory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)


def SaveConversation(user_msg, assistant_msg):
    memory = LoadMemory()
    memory["conversations"].append({
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_msg,
        "assistant": assistant_msg
    })
    SaveMemory(memory)


# ===============================
# AUTO FACT LEARNING
# ===============================
def AutoExtractFacts(text):
    memory = LoadMemory()
    facts = memory["facts"]
    t = text.lower()
    patterns = [
        (r"\bi am (\w+)", "name"),
        (r"\bi'm (\w+)", "name"),
        (r"\bmy name is (\w+)", "name"),
        (r"\bcall me (\w+)", "name"),
        (r"\bthis is (\w+)", "name"),
        (r"\bmy favorite language is ([a-zA-Z]+)", "favorite_language"),
        (r"\bi study ([a-zA-Z ]+)", "field_of_study"),
        (r"\bi live in ([a-zA-Z ]+)", "location"),
        (r"\bmy project is ([a-zA-Z0-9 ]+)", "project"),
    ]
    for pattern, key in patterns:
        match = re.search(pattern, t)
        if match:
            facts[key] = match.group(1).strip().title()
    SaveMemory(memory)


# ===============================
# MEMORY RECALL
# ===============================
def RecallFact(query):
    memory = LoadMemory()
    facts = memory["facts"]
    q = query.lower()
    if "name" in q and ("my" in q or "i" in q):
        if "name" in facts:
            return f"Your name is {facts['name']}."
    if "favorite" in q and "language" in q:
        if "favorite_language" in facts:
            return f"Your favorite language is {facts['favorite_language']}."
    if "study" in q:
        if "field_of_study" in facts:
            return f"You study {facts['field_of_study']}."
    if "live" in q or "location" in q:
        if "location" in facts:
            return f"You live in {facts['location']}."
    if "project" in q:
        if "project" in facts:
            return f"Your project is {facts['project']}."
    return None


def GetMemoryContext():
    memory = LoadMemory()
    facts = memory["facts"]
    if not facts:
        return ""
    context = "Known facts about the user:\n"
    for k, v in facts.items():
        context += f"- {k.replace('_', ' ').capitalize()}: {v}\n"
    return context.strip()


# ===============================
# UTILITIES
# ===============================
def RealtimeInformation():
    now = datetime.datetime.now()
    today = now.strftime("%B %d, %Y")  # e.g., December 25, 2025
    time = now.strftime("%H:%M:%S")
    return f"*** CURRENT REAL-WORLD DATE AND TIME: {today} | {time} ***\nUse this date for all time-related answers."


def AnswerModifier(text):
    if not text:
        return ""
    return "\n".join(line for line in text.strip().split("\n") if line.strip())


# ===============================
# CHAT HISTORY
# ===============================
chat_history = []


# ===============================
# AI FUNCTIONS (CUTOFF FIXED)
# ===============================
def GroqChat():
    global chat_history
    answer = ""
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.3-70b-specdec",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it"
    ]
    system_message = {"role": "system",
                      "content": SYSTEM_PROMPT + "\n" + GetMemoryContext() + "\n" + RealtimeInformation()}
    for model in models:
        try:
            stream = groq_client.chat.completions.create(
                model=model,
                messages=[system_message] + chat_history,
                stream=True,
                temperature=0.7,
                max_tokens=1024
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content
            return AnswerModifier(answer)
        except Exception as e:
            print(f"Groq model {model} failed: {e}")
            continue
    raise RuntimeError("All Groq models failed")


def OpenAIChat():
    global chat_history
    system_message = {"role": "system",
                      "content": SYSTEM_PROMPT + "\n" + GetMemoryContext() + "\n" + RealtimeInformation()}
    messages = [system_message] + chat_history
    res = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return AnswerModifier(res.choices[0].message.content)


def GeminiChat(query):
    full_prompt = (
        f"{SYSTEM_PROMPT}\n"
        f"{GetMemoryContext()}\n"
        f"{RealtimeInformation()}\n"
        "Conversation so far:\n"
    )
    for msg in chat_history[-15:]:
        role = "User" if msg["role"] == "user" else Assistantname
        full_prompt += f"{role}: {msg['content']}\n"
    full_prompt += f"User: {query}\n{Assistantname}:"

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt
    )
    return AnswerModifier(response.text)


def CohereChat(query):
    chat_hist = []
    for msg in chat_history:
        role = "USER" if msg["role"] == "user" else "CHATBOT"
        chat_hist.append({"role": role, "message": msg["content"]})

    res = cohere_client.chat(
        model="command-r-plus",
        message=query,
        chat_history=chat_hist,
        preamble=SYSTEM_PROMPT + "\n" + GetMemoryContext() + "\n" + RealtimeInformation()
    )
    return AnswerModifier(res.text)


# ===============================
# MAIN CHATBOT
# ===============================
def ChatBot(query):
    global chat_history
    q = query.strip()
    if not q:
        return "Please type something!"
    AutoExtractFacts(q)
    recall = RecallFact(q)
    if recall:
        chat_history.append({"role": "user", "content": q})
        chat_history.append({"role": "assistant", "content": recall})
        SaveConversation(q, recall)
        return recall
    chat_history.append({"role": "user", "content": q})
    try:
        ans = GroqChat()
    except:
        try:
            ans = OpenAIChat()
        except:
            try:
                ans = GeminiChat(q)
            except:
                ans = CohereChat(q)
    ans = AnswerModifier(ans)
    chat_history.append({"role": "assistant", "content": ans})
    AutoExtractFacts(ans)
    SaveConversation(q, ans)
    return ans


# ===============================
# CLI LOOP
# ===============================
if __name__ == "__main__":
    print(f"\n🤖 {Assistantname} ready, {Username}! (Full memory + No cutoff lies 🔥)\n")
    memory = LoadMemory()
    recent = memory["conversations"][-15:]
    for conv in recent:
        chat_history.append({"role": "user", "content": conv["user"]})
        chat_history.append({"role": "assistant", "content": conv["assistant"]})

    while True:
        q = input(f"{Username} > ")
        if q.lower() in ["quit", "exit", "bye", "clear"]:
            if q.lower() == "clear":
                chat_history.clear()
                print(f"{Assistantname} > Memory cleared! Starting fresh.\n")
                continue
            print(f"{Assistantname} > Bye {Username}! Take care ❤️")
            break
        res = ChatBot(q)
        print(f"{Assistantname} > {res}\n")




