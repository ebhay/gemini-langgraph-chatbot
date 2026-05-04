import { useState, useEffect, useRef } from "react";

function Sidebar({ chats, currentChatId, setCurrentChatId, newChat, deleteChat, toggleProfile }) {
  const [activeMenuId, setActiveMenuId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [chatToDelete, setChatToDelete] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const menuRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setActiveMenuId(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const openDeleteModal = (id) => {
    setChatToDelete(id);
    setShowDeleteModal(true);
    setActiveMenuId(null);
  };

  const confirmDelete = () => {
    if (chatToDelete) {
      deleteChat(chatToDelete);
      setActiveMenuId(null); // Ensure menu closes
    }
    setShowDeleteModal(false);
    setChatToDelete(null);
  };

  // Notification Polling
  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const res = await fetch(`${process.env.REACT_APP_API_URL}/notifications`);
        if (res.ok) {
          const data = await res.json();
          setNotifications(data);
        }
      } catch (err) {
        console.error("Failed to fetch notifications:", err);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 10000); // every 10s
    return () => clearInterval(interval);
  }, []);

  const dismissNotification = async (id) => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL}/notifications/read/${id}`, { method: "POST" });
      setNotifications(notifications.filter(n => n.id !== id));
    } catch (err) {
      console.error("Failed to dismiss notification:", err);
    }
  };

  return (
    <>
      <div style={{
        width: "250px",
        background: "#f3f4f6",
        borderRight: "1px solid #e5e7eb",
        padding: "12px",
        display: "flex",
        flexDirection: "column",
        height: "100vh"
      }}>

        {notifications.length > 0 && (
          <div style={{ marginBottom: "20px" }}>
            <div style={{ fontSize: "12px", fontWeight: "bold", color: "#fb923c", marginBottom: "8px" }}>
              NOTIFICATIONS ({notifications.length})
            </div>
            {notifications.map(n => (
              <div key={n.id} style={{ 
                background: "#fffbeb", 
                border: "1px solid #fef3c7", 
                padding: "8px", 
                borderRadius: "6px",
                fontSize: "12px",
                marginBottom: "6px",
                position: "relative"
              }}>
                {n.message}
                <button 
                  onClick={() => dismissNotification(n.id)}
                  style={{
                    position: "absolute",
                    right: "4px",
                    top: "4px",
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                    fontSize: "10px"
                  }}
                >✕</button>
              </div>
            ))}
          </div>
        )}

        <button onClick={newChat} style={{ 
          width: "100%", 
          marginBottom: "10px",
          padding: "10px",
          borderRadius: "8px",
          border: "1px solid #e5e7eb",
          background: "white",
          cursor: "pointer",
          fontWeight: "600"
        }}>
          + New Chat
        </button>

        <button onClick={toggleProfile} style={{ 
          width: "100%", 
          marginBottom: "20px",
          padding: "10px",
          borderRadius: "8px",
          border: "1px solid #fb923c",
          background: "#fff7ed",
          color: "#ea580c",
          cursor: "pointer",
          fontWeight: "600"
        }}>
          👤 My Profile
        </button>

        <div style={{ flex: 1, overflowY: "auto" }}>
          {chats.map((chat) => (
            <div
              key={chat.id}
              className="sidebar-item"
              onClick={() => setCurrentChatId(chat.id)}
              style={{
                padding: "10px",
                borderRadius: "8px",
                marginBottom: "6px",
                cursor: "pointer",
                background: chat.id === currentChatId ? "#e5e7eb" : "transparent",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}
            >
              <span style={{ 
                whiteSpace: "nowrap", 
                overflow: "hidden", 
                textOverflow: "ellipsis",
                fontSize: "14px",
                maxWidth: "160px"
              }}>
                {chat.title}
              </span>

              <span
                className="menu-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveMenuId(activeMenuId === chat.id ? null : chat.id);
                }}
                style={{ padding: "0 5px", fontSize: "18px" }}
              >
                ⋮
              </span>

              {activeMenuId === chat.id && (
                <div className="dropdown-menu" ref={menuRef}>
                  <div 
                    className="dropdown-item delete" 
                    onClick={(e) => {
                      e.stopPropagation();
                      openDeleteModal(chat.id);
                    }}
                  >
                    🗑️ Delete
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Custom Delete Modal */}
      {showDeleteModal && (
        <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="modal-title">Delete Chat?</div>
            <div className="modal-text">This will permanently delete this conversation and its history.</div>
            <div className="modal-buttons">
              <button className="btn btn-cancel" onClick={() => setShowDeleteModal(false)}>Cancel</button>
              <button className="btn btn-delete" onClick={confirmDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Sidebar;