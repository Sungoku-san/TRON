"use client";

import { useState } from "react";
import "./globals.css";

export default function Page() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<string[]>([
    "Hello, MR.STARK."
  ]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, `You: ${input}`]);

    try {
      const res = await fetch("http://127.0.0.1:8000/tron", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();
      setMessages((prev) => [...prev, `TRON: ${data.reply}`]);
    } catch {
      setMessages((prev) => [...prev, "⚠️ Unable to reach TRON backend."]);
    }

    setInput("");
  };

  return (
    <div className="app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <h2>TRON</h2>
        <button className="new-chat">＋ New chat</button>

        <div className="section">
          <p>My stuff</p>
          <div className="item">⚙️ System Logs</div>
          <div className="item">📊 Analytics</div>
        </div>

        <div className="section">
          <p>Chats</p>
          <div className="item">AI Startup Idea</div>
          <div className="item">Vision Detection</div>
          <div className="item">Settings & Help</div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main">
        <div className="center">
          <h1>✨ Hi, MR.STARK</h1>
          <h3>Where should we start?</h3>

          {/* OUTPUT BOX */}
          <div className="chatbox" id="chatbox">
            {messages.map((msg, i) => (
              <div key={i}>{msg}</div>
            ))}
          </div>

          {/* INPUT BOX */}
          <div className="chat-input">
            <button className="mic-btn">🎙️</button>

            <input
              type="text"
              placeholder="Ask TRON anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />

            <button className="send-btn" onClick={sendMessage}>
              ➤
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}