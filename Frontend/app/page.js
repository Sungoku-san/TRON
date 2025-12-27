'use client'

import { useState, useRef, useEffect } from 'react'

export default function Home() {
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState([]) // Now stores full chat history
  const [isLoading, setIsLoading] = useState(false)
  const [voiceMode, setVoiceMode] = useState(false)
  const recognitionRef = useRef(null)
  const utterRef = useRef(null)
  const messagesEndRef = useRef(null)

  const SLEEP_WORD = "shutdown tron"

  // Auto-scroll to bottom when new message arrives
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // ===============================
  // SEND MESSAGE (text or voice)
  // ===============================
  const sendMessage = async (text) => {
    if (!text.trim()) return

    const userMessage = text.trim()
    setMessages(prev => [...prev, { role: "user", content: userMessage }])
    setIsLoading(true)

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
      })
      const data = await res.json()

      let reply = data.reply || "No response."

      // Hide the ugly "i remain silent" message
      if (reply.toLowerCase().includes("i remain silent")) {
        reply = "I'm thinking... Let me get back to you with a proper response."
      }

      setMessages(prev => [...prev, { role: "assistant", content: reply }])

      if (voiceMode) playAudioReply(reply)
    } catch (err) {
      const errorMsg = "Connection failed. Is the backend running on port 8000?"
      setMessages(prev => [...prev, { role: "assistant", content: errorMsg }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSend = () => {
    if (!input.trim()) return
    sendMessage(input)
    setInput("")
  }

  // ===============================
  // TTS AUDIO PLAYBACK
  // ===============================
  const playAudioReply = async (text) => {
    if (!voiceMode) return

    // Cancel previous speech
    if (utterRef.current instanceof Audio) {
      utterRef.current.pause()
      utterRef.current.currentTime = 0
    } else if (utterRef.current instanceof SpeechSynthesisUtterance) {
      window.speechSynthesis.cancel()
    }

    try {
      const res = await fetch("http://localhost:8000/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text })
      })
      const data = await res.json()
      if (data.audio_base64) {
        const audio = new Audio("data:audio/mp3;base64," + data.audio_base64)
        utterRef.current = audio
        audio.play().catch(() => fallbackTTS(text))
      } else {
        fallbackTTS(text)
      }
    } catch (e) {
      fallbackTTS(text)
    }
  }

  const fallbackTTS = (text) => {
    const synth = window.speechSynthesis
    const utter = new SpeechSynthesisUtterance(text)
    utter.rate = 0.95
    utter.pitch = 1.0
    utterRef.current = utter
    synth.speak(utter)
  }

  // ===============================
  // VOICE MODE
  // ===============================
  const startVoiceMode = () => {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Voice mode requires Chrome or Edge browser.")
      return
    }

    const recognition = new window.webkitSpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = false
    recognition.lang = "en-IN"

    recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim()
      console.log("Heard:", transcript)

      if (transcript.toLowerCase().includes(SLEEP_WORD)) {
        stopVoiceMode()
        playAudioReply("Voice mode disabled. Goodbye.")
        return
      }

      if (transcript) {
        sendMessage(transcript)
      }
    }

    recognition.onend = () => {
      if (voiceMode) recognition.start()
    }

    recognition.start()
    recognitionRef.current = recognition
    setVoiceMode(true)
    playAudioReply("Voice mode activated. I'm listening.")
  }

  const stopVoiceMode = () => {
    recognitionRef.current?.stop()
    recognitionRef.current = null
    setVoiceMode(false)
    window.speechSynthesis.cancel()
    if (utterRef.current instanceof Audio) {
      utterRef.current.pause()
    }
    utterRef.current = null
  }

  // ===============================
  // UI
  // ===============================
  return (
    <main className="container">
      <h1 className="title">TRON v2</h1>
      <p className="subtitle">
        {voiceMode ? "🎤 Voice mode active" : "🟡 Click mic to enable voice"}
      </p>

      <div className="chat-container" style={{
        maxHeight: "60vh",
        overflowY: "auto",
        padding: "10px",
        marginBottom: "20px"
      }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              margin: "10px 0",
              padding: "12px 16px",
              borderRadius: "12px",
              maxWidth: "80%",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              background: msg.role === "user" ? "#0070f3" : "#1a1a1a",
              color: "#fff",
              marginLeft: msg.role === "user" ? "auto" : "0",
              marginRight: msg.role === "user" ? "0" : "auto",
              whiteSpace: "pre-wrap",
              fontFamily: "system-ui, sans-serif",
              lineHeight: "1.5"
            }}
          >
            {msg.content}
          </div>
        ))}

        {isLoading && (
          <div style={{
            padding: "12px 16px",
            color: "#aaa",
            fontStyle: "italic"
          }}>
            Thinking...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="inputBox">
        <input
          placeholder="Ask anything..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && !e.shiftKey && handleSend()}
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading}>✈️</button>
        <button onClick={voiceMode ? stopVoiceMode : startVoiceMode}>
          {voiceMode ? "🛑 Stop Voice" : "🎤 Voice On"}
        </button>
      </div>

      <style jsx>{`
        .container {
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          font-family: system-ui, sans-serif;
        }
        .title {
          font-size: 2.5rem;
          text-align: center;
          margin-bottom: 10px;
          color: #fff;
        }
        .subtitle {
          text-align: center;
          color: #ccc;
          margin-bottom: 20px;
        }
        .chat-container {
          background: #0d0d0d;
          border-radius: 12px;
          display: flex;
          flex-direction: column;
        }
        .inputBox {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }
        .inputBox input {
          flex: 1;
          padding: 14px;
          border-radius: 12px;
          border: 1px solid #333;
          background: #1a1a1a;
          color: white;
          font-size: 1rem;
        }
        .inputBox button {
          padding: 0 20px;
          border-radius: 12px;
          background: #0070f3;
          color: white;
          border: none;
          cursor: pointer;
          font-size: 1.2rem;
        }
        .inputBox button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </main>
  )
}