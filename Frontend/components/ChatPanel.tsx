type Message = {
  role: "user" | "assistant"
  text: string
}

export default function ChatPanel({ messages }: { messages: Message[] }) {
  return (
    <div className="w-full max-w-xl h-[55vh] overflow-y-auto px-4 py-3 space-y-3">
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`px-4 py-2 rounded-xl max-w-[80%] ${
            msg.role === "user"
              ? "ml-auto bg-blue-600"
              : "mr-auto bg-gray-800"
          }`}
        >
          {msg.text}
        </div>
      ))}
    </div>
  )
}