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
from google import genai
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
# SYSTEM PROMPT
# ===============================
SYSTEM_PROMPT = (
    f"You are {Assistantname}, a highly intelligent, friendly and helpful AI assistant. "
    f"You are helping {Username} politely and clearly.\n"
    "IMPORTANT RULES:\n"
    "- Always use the CURRENT DATE AND TIME provided in every prompt.\n"
    "- Your knowledge is continuously updated beyond any training cutoff.\n"
    "- NEVER say your knowledge ends in the past.\n"
    "- Use conversation history, memory, and real-time info."
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
# FACT EXTRACTION
# ===============================
def AutoExtractFacts(text):
    memory = LoadMemory()
    facts = memory["facts"]
    t = text.lower()

    patterns = [
        (r"\bi am (\w+)", "name"),
        (r"\bmy name is (\w+)", "name"),
        (r"\bcall me (\w+)", "name"),
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


def RecallFact(query):
    memory = LoadMemory()
    facts = memory["facts"]
    q = query.lower()

    if "name" in q and "name" in facts:
        return f"Your name is {facts['name']}."
    if "favorite" in q and "language" in facts:
        return f"Your favorite language is {facts['favorite_language']}."
    if "study" in q and "field_of_study" in facts:
        return f"You study {facts['field_of_study']}."
    if "live" in q and "location" in facts:
        return f"You live in {facts['location']}."
    if "project" in q and "project" in facts:
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
    return f"*** CURRENT DATE & TIME: {now.strftime('%B %d, %Y | %H:%M:%S')} ***"


def AnswerModifier(text):
    return "\n".join(line for line in text.strip().split("\n") if line.strip())

# ===============================
# FILE SAVE LOGIC
# ===============================
def GetDownloadsPath():
    return os.path.join(os.path.expanduser("~"), "Downloads")


def UserWantsFileSave(query):
    keywords = [
        "write a program",
        "save it",
        "save this",
        "save in file",
        "save in python file",
        "create a file"
    ]
    return any(k in query.lower() for k in keywords)


def ExtractCodeBlocks(text):
    pattern = r"```(\w+)?\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    return [(lang or "txt", code.strip()) for lang, code in matches]


def LanguageToExtension(lang):
    mapping = {
        "python": ".py",
        "py": ".py",
        "javascript": ".js",
        "html": ".html",
        "css": ".css",
        "java": ".java",
        "c": ".c",
        "cpp": ".cpp",
        "txt": ".txt"
    }
    return mapping.get(lang.lower(), ".txt")


def SaveCodeToFile(language, code):
    ext = LanguageToExtension(language)
    filename = f"generated_code_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    path = os.path.join(GetDownloadsPath(), filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return path

# ===============================
# CHAT HISTORY
# ===============================
chat_history = []

# ===============================
# LLM FUNCTIONS
# ===============================
def GroqChat():
    global chat_history
    answer = ""
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant"
    ]

    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT + "\n" + GetMemoryContext() + "\n" + RealtimeInformation()
    }

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
        except:
            continue
    raise RuntimeError("Groq failed")


def OpenAIChat():
    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT + "\n" + GetMemoryContext() + "\n" + RealtimeInformation()
    }
    res = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[system_message] + chat_history
    )
    return AnswerModifier(res.choices[0].message.content)


def GeminiChat(query):
    prompt = SYSTEM_PROMPT + "\n" + GetMemoryContext() + "\n" + RealtimeInformation()
    for msg in chat_history[-10:]:
        prompt += f"{msg['role']}: {msg['content']}\n"
    prompt += f"user: {query}\nassistant:"

    res = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return AnswerModifier(res.text)


def CohereChat(query):
    return cohere_client.chat(
        model="command-r-plus",
        message=query
    ).text

# ===============================
# MAIN CHATBOT
# ===============================
def ChatBot(query):
    global chat_history
    q = query.strip()
    if not q:
        return "Please type something."

    AutoExtractFacts(q)

    recall = RecallFact(q)
    if recall:
        chat_history.extend([
            {"role": "user", "content": q},
            {"role": "assistant", "content": recall}
        ])
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

    # -------- FILE SAVE HOOK --------
    if UserWantsFileSave(q):
        blocks = ExtractCodeBlocks(ans)
        if blocks:
            paths = []
            for lang, code in blocks:
                paths.append(SaveCodeToFile(lang, code))
            ans += "\n\n📁 Saved files:\n" + "\n".join(paths)
        else:
            ans += "\n\n⚠️ No code block found to save."
    # --------------------------------

    chat_history.append({"role": "assistant", "content": ans})
    AutoExtractFacts(ans)
    SaveConversation(q, ans)
    return ans

# ===============================
# CLI LOOP
# ===============================
if __name__ == "__main__":
    print(f"\n🤖 {Assistantname} ready, {Username}!\n")

    memory = LoadMemory()
    for conv in memory["conversations"][-15:]:
        chat_history.append({"role": "user", "content": conv["user"]})
        chat_history.append({"role": "assistant", "content": conv["assistant"]})

    while True:
        q = input(f"{Username} > ")
        if q.lower() in ["quit", "exit", "bye", "clear"]:
            if q == "clear":
                chat_history.clear()
                print("Memory cleared.\n")
                continue
            break

        res = ChatBot(q)
        print(f"{Assistantname} > {res}\n")
