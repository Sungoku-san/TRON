async function sendMessage() {
  const input = document.querySelector(".chat-input input");
  const chatbox = document.getElementById("chatbox");

  const message = input.value.trim();
  if (!message) return;

  // Show user message
  chatbox.innerHTML += `\nYou: ${message}\n`;
  chatbox.scrollTop = chatbox.scrollHeight;
  input.value = "";

  try {
    const response = await fetch("http://127.0.0.1:8000/tron", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    });

    const data = await response.json();

    chatbox.innerHTML += `TRON: ${data.reply}\n\n`;
    chatbox.scrollTop = chatbox.scrollHeight;

  } catch (error) {
    chatbox.innerHTML += "⚠️ Unable to connect to TRON backend.\n";
  }
}

/* ENTER KEY SUPPORT */
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendMessage();
  }
});