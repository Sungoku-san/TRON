import sqlite3
import datetime
import os
from typing import List, Dict

DB_PATH = "tron_conversations.db"


def init_db():
    """Create the database and table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        speaker TEXT NOT NULL,  -- 'user' or 'tron'
        message TEXT NOT NULL,
        language TEXT  -- 'en', 'hi', 'te', 'ta' or detected code
    )
    ''')
    conn.commit()
    conn.close()
    print(f"[DB] Database ready at {os.path.abspath(DB_PATH)}")


def log_message(speaker: str, message: str, language: str = "en"):
    """Log a single message to the database."""
    if not message.strip():
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO conversations (timestamp, speaker, message, language) VALUES (?, ?, ?, ?)",
              (timestamp, speaker.lower(), message.strip(), language.lower()))
    conn.commit()
    conn.close()


def get_conversation_history(limit: int = 50) -> List[Dict]:
    """Get recent conversation history (latest first)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, speaker, message, language FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()

    history = []
    for row in reversed(rows):  # Reverse to chronological order
        history.append({
            "timestamp": row[0],
            "speaker": row[1],
            "message": row[2],
            "language": row[3]
        })
    return history


def clear_history():
    """Clear all conversation history (optional command)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()
    print("[DB] Conversation history cleared.")


# Initialize on import
init_db()