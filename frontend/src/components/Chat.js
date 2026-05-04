import { useState, useRef, useEffect } from "react";
import "../styles.css";

function Chat({ messages, setMessages }) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };

    // add user message
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_input: input }),
      });

      const data = await res.json();

      // add bot response
      setMessages([
        ...updatedMessages,
        { role: "bot", text: data.response },
      ]);

    } catch (err) {
      setMessages([
        ...updatedMessages,
        { role: "bot", text: "Error connecting to server." },
      ]);
    }

    setInput("");
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
          <div ref={messagesEndRef} />
        </div>

        <div className="input-wrapper">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything"
            onKeyDown={(e) => {
              if (e.key === "Enter") sendMessage(); // ✅ Enter key support
            }}
          />
          <button onClick={sendMessage}>➤</button>
        </div>

      </div>
    </div>
  );
}

export default Chat;