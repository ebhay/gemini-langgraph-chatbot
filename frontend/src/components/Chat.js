import { useState, useRef, useEffect } from "react";
import "../styles.css";

function Chat({ messages, setMessages, sessionId }) {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (messages.length > 0) {
      scrollToBottom();
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = { role: "user", text: input };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput("");
    setIsLoading(true);

try {
  const res = await fetch(`${process.env.REACT_APP_API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ 
      user_input: userMsg.text,
      session_id: sessionId 
    }),
  });

  if (!res.ok) {
    throw new Error(`Server error: ${res.status}`);
  }

  const data = await res.json();

  setMessages([
    ...updatedMessages,
    { role: "bot", text: data.response || "No response from server" },
  ]);

} catch (err) {
  console.error("API Error:", err);

  setMessages([
    ...updatedMessages,
    { role: "bot", text: "Error connecting to server." },
  ]);
} finally {
  setIsLoading(false);
}

  };

  const isStarted = messages.length > 0;

  return (
    <div className={`container ${isStarted ? "chat-started" : ""}`}>

      {!isStarted && (
        <div className="greeting">How can I help you today?</div>
      )}

      <div className="chat-box">

        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div className="message bot thinking">Thinking...</div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-wrapper">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isLoading ? "Waiting for response..." : "Ask anything"}
            disabled={isLoading}
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage();
            }}
          />
          <button onClick={sendMessage} disabled={isLoading}>
            {isLoading ? "⏳" : "➤"}
          </button>
        </div>

      </div>
    </div>
  );
}

export default Chat;