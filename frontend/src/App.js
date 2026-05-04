import { useState, useEffect } from "react";
import Chat from "./components/Chat";
import Sidebar from "./components/Sidebar";
import "./styles.css";

function App() {
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [profile, setProfile] = useState({});
  const [editingKey, setEditingKey] = useState(null);
  const [editingValue, setEditingValue] = useState("");

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/sessions`);
      if (res.ok) {
        const data = await res.json();
        if (data && data.length > 0) {
          const mapped = data.map(s => ({
            id: s.id,
            title: s.first_message
              ? s.first_message.slice(0, 30) + (s.first_message.length > 30 ? "..." : "")
              : `Session ${s.id.slice(0, 8)}...`,
            messages: []
          }));
          setChats(mapped);
          setCurrentChatId(prev => {
            if (prev && mapped.find(c => c.id === prev)) return prev;
            return mapped[0].id;
          });
        } else {
          const newId = `session_${Date.now()}`;
          setChats([{ id: newId, title: "New Chat", messages: [] }]);
          setCurrentChatId(newId);
        }
      }
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    const fetchHistory = async () => {
      if (!currentChatId) return;
      const activeChat = chats.find(c => c.id === currentChatId);
      if (activeChat && activeChat.messages.length === 0) {
        try {
          const res = await fetch(`${process.env.REACT_APP_API_URL}/sessions/${currentChatId}`);
          if (res.ok) {
            const history = await res.json();
            setChats(prev => prev.map(c =>
              c.id === currentChatId ? { ...c, messages: history } : c
            ));
          }
        } catch (err) {
          console.error("Failed to fetch history:", err);
        }
      }
    };
    fetchHistory();
  }, [currentChatId, chats]);

  const fetchProfile = async () => {
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/profile`);
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
    }
  };

  const saveProfileEdit = async (key) => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL}/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value: editingValue }),
      });
      setProfile(prev => ({ ...prev, [key]: editingValue }));
      setEditingKey(null);
      setEditingValue("");
    } catch (err) {
      console.error("Failed to save profile edit:", err);
    }
  };

  const toggleProfile = () => {
    if (!showProfile) fetchProfile();
    setShowProfile(!showProfile);
    setEditingKey(null);
  };

  const currentChat = chats.find(c => c.id === currentChatId) || { id: "new", title: "New Chat", messages: [] };

  const newChat = () => {
    const newId = `session_${Date.now()}`;
    setChats([{ id: newId, title: "New Chat", messages: [] }, ...chats]);
    setCurrentChatId(newId);
  };

  const deleteChat = async (id) => {
    setChats(prev => prev.filter(c => c.id !== id));
    if (currentChatId === id) {
      const remaining = chats.filter(c => c.id !== id);
      setCurrentChatId(remaining.length > 0 ? remaining[0].id : null);
    }
    try {
      await fetch(`${process.env.REACT_APP_API_URL}/sessions/${id}`, { method: "DELETE" });
      await fetchSessions();
      setChats(prev => {
        if (prev.length === 0) {
          const newId = `session_${Date.now()}`;
          setCurrentChatId(newId);
          return [{ id: newId, title: "New Chat", messages: [] }];
        }
        return prev;
      });
    } catch (err) {
      console.error("Failed to clear session:", err);
    }
  };

  const updateMessages = (newMessages) => {
    setChats(chats.map(chat => {
      if (chat.id !== currentChatId) return chat;
      const firstUserMsg = newMessages.find(m => m.role === "user");
      const isDefaultTitle = chat.title === "New Chat" || chat.title === "Chat" || chat.title.startsWith("Session ");
      const title = (isDefaultTitle && firstUserMsg)
        ? firstUserMsg.text.slice(0, 30) + (firstUserMsg.text.length > 30 ? "..." : "")
        : chat.title;
      return { ...chat, messages: newMessages, title };
    }));
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar
        chats={chats}
        currentChatId={currentChatId}
        setCurrentChatId={setCurrentChatId}
        newChat={newChat}
        deleteChat={deleteChat}
        toggleProfile={toggleProfile}
      />

      {showProfile ? (
        <div className="container profile-view">
          <div className="chat-box" style={{ padding: "40px", overflowY: "auto" }}>
            <h1 className="greeting" style={{ fontSize: "28px", marginBottom: "6px" }}>Your Profile</h1>
            <p style={{ color: "#9ca3af", fontSize: "13px", marginBottom: "24px" }}>
              Facts the bot has learned about you. Click ✏️ to edit any value.
            </p>

            <div className="profile-details">
              {Object.keys(profile).length > 0 ? (
                Object.entries(profile).map(([k, v]) => (
                  <div key={k} className="profile-item">
                    <span className="profile-key" style={{ minWidth: "100px" }}>{k}</span>

                    {editingKey === k ? (
                      <div style={{ display: "flex", gap: "8px", flex: 1 }}>
                        <input
                          className="profile-edit-input"
                          value={editingValue}
                          onChange={e => setEditingValue(e.target.value)}
                          onKeyDown={e => {
                            if (e.key === "Enter") saveProfileEdit(k);
                            if (e.key === "Escape") setEditingKey(null);
                          }}
                          autoFocus
                        />
                        <button className="btn btn-save" onClick={() => saveProfileEdit(k)}>Save</button>
                        <button className="btn btn-cancel" onClick={() => setEditingKey(null)}>✕</button>
                      </div>
                    ) : (
                      <div style={{ display: "flex", alignItems: "center", gap: "12px", flex: 1 }}>
                        <span className="profile-value">{v}</span>
                        <button
                          className="btn-edit-icon"
                          onClick={() => { setEditingKey(k); setEditingValue(v); }}
                          title="Edit"
                        >✏️</button>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p style={{ color: "#9ca3af" }}>No facts known yet. Talk to the bot!</p>
              )}
            </div>

            <button className="btn btn-cancel" onClick={() => setShowProfile(false)} style={{ marginTop: "28px" }}>
              ← Back to Chat
            </button>
          </div>
        </div>
      ) : (
        <Chat
          messages={currentChat.messages}
          setMessages={updateMessages}
          sessionId={currentChatId}
        />
      )}
    </div>
  );
}

export default App;