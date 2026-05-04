import { useState, useEffect, useRef } from "react";

function Sidebar({ chats, currentChatId, setCurrentChatId, newChat, deleteChat }) {
  const [activeMenuId, setActiveMenuId] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [chatToDelete, setChatToDelete] = useState(null);
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
    }
    setShowDeleteModal(false);
    setChatToDelete(null);
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

        <button onClick={newChat} style={{ 
          width: "100%", 
          marginBottom: "20px",
          padding: "10px",
          borderRadius: "8px",
          border: "1px solid #e5e7eb",
          background: "white",
          cursor: "pointer",
          fontWeight: "600"
        }}>
          + New Chat
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
                <div className="dropdown-menu" ref={menuRef} onClick={(e) => e.stopPropagation()}>
                  <div 
                    className="dropdown-item delete" 
                    onClick={() => openDeleteModal(chat.id)}
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