import { useState, useEffect } from "react";
import Chat from "./components/Chat";
import Sidebar from "./components/Sidebar";
import "./styles.css";

function App() {
  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem("chatbot_chats");
    return saved ? JSON.parse(saved) : [{ id: 1, title: "New Chat", messages: [] }];
  });

  const [currentChatId, setCurrentChatId] = useState(() => {
    const saved = localStorage.getItem("chatbot_current_id");
    return saved ? JSON.parse(saved) : 1;
  });

  useEffect(() => {
    localStorage.setItem("chatbot_chats", JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    localStorage.setItem("chatbot_current_id", JSON.stringify(currentChatId));
  }, [currentChatId]);

  const currentChat = chats.find(c => c.id === currentChatId) || chats[0];

  const newChat = () => {
    const newId = Date.now();
    setChats([...chats, { id: newId, title: "New Chat", messages: [] }]);
    setCurrentChatId(newId);
  };

  const deleteChat = (id) => {
    const updated = chats.filter(chat => chat.id !== id);
    if (updated.length === 0) {
      const fresh = { id: Date.now(), title: "New Chat", messages: [] };
      setChats([fresh]);
      setCurrentChatId(fresh.id);
    } else {
      setChats(updated);
      if (currentChatId === id) {
        setCurrentChatId(updated[0].id);
      }
    }
  };

  const updateMessages = (newMessages) => {
    setChats(chats.map(chat =>
      chat.id === currentChatId
        ? { ...chat, messages: newMessages }
        : chat
    ));
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        setCurrentChatId={setCurrentChatId}
        newChat={newChat}
        deleteChat={deleteChat}
      />

      <Chat
        messages={currentChat.messages}
        setMessages={updateMessages}
      />

    </div>
  );
}

export default App;