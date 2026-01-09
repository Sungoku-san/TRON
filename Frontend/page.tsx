"use client";

import { useState, useRef, useEffect } from "react";

export default function Page() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "tron"; text: string }[]>([
    { role: "tron", text: "Tron is online. Press and hold 🎤 to talk." },
  ]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false); // New: show when TRON speaks
  const [currentLang, setCurrentLang] = useState("en"); // Track language for mic

  const chatRef = useRef<HTMLDivElement>(null);
  let recognition: any = null;

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userText = text.trim();
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setInput("");

    try {
      const res = await fetch("http://127.0.0.1:8000/tron", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }),
      });

      if (!res.ok) throw new Error("Backend error");

      const data = await res.json();
      const reply = data.reply;

      setMessages((prev) => [...prev, { role: "tron", text: reply }]);

      // Auto-speak reply
      setIsSpeaking(true);
      await fetch("http://127.0.0.1:8000/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: reply }),
      });
      setIsSpeaking(false);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "tron", text: "⚠️ Cannot connect to TRON." }]);
      setIsSpeaking(false);
    }
  };

  const startListening = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition not supported. Use Chrome desktop.");
      return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = currentLang === "hi" ? "hi-IN" : "en-IN"; // Auto-match language
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      sendMessage(transcript);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);

    recognition.start();
  };

  const stopListening = () => {
    if (recognition) recognition.stop();
  };

  return (
    <div className="app">
      <main className="main">
        <div className="center">
          <h1>✨ TRON V2</h1>
          <h3>TRON Voice Assistant</h3>

          <div className="chatbox" ref={chatRef}>
            {messages.map((msg, i) => (
              <div key={i} className={msg.role === "tron" ? "tron-msg" : "user-msg"}>
                <strong>{msg.role === "user" ? "You" : "TRON"}:</strong> {msg.text}
                {msg.role === "tron" && isSpeaking && <span> 🔊 Speaking...</span>}
              </div>
            ))}
          </div>

          <div className="chat-input">
            <button
              className={`mic-btn ${isListening ? "listening" : ""}`}
              onMouseDown={startListening}
              onMouseUp={stopListening}
              onMouseLeave={stopListening}
              onTouchStart={startListening}
              onTouchEnd={stopListening}
              title="Press and hold to talk to TRON"
              disabled={isSpeaking} // Optional: disable during speaking
            >
              {isListening ? "🎤 Listening..." : isSpeaking ? "🔊 TRON speaking..." : "🎤 Hold to Talk"}
            </button>

            <input
              type="text"
              placeholder="Or type here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
            />

            <button className="send-btn" onClick={() => sendMessage(input)}>
              ➤
            </button>
          </div>

          <p className="tip">
            💡 Hold 🎤 to speak • TRON replies & speaks back automatically
          </p>
        </div>
      </main>
    </div>
  );
}
