import React, { useEffect } from "react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(0, 0, 0, 0.65)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: "1rem",
        fontFamily: "sans-serif",
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: "var(--code-bg, #1f2028)",
          color: "var(--text-h, #f3f4f6)",
          borderRadius: "8px",
          width: "100%",
          maxWidth: "550px",
          maxHeight: "90vh",
          overflowY: "auto",
          boxShadow: "0 10px 25px rgba(0, 0, 0, 0.4)",
          border: "1px solid var(--border, #2e303a)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "15px 20px",
            borderBottom: "1px solid var(--border, #2e303a)",
          }}
        >
          <h3 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 600, color: "var(--text-h, #f3f4f6)" }}>
            {title}
          </h3>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              color: "var(--text, #9ca3af)",
              fontSize: "1.5rem",
              cursor: "pointer",
              lineHeight: 1,
              padding: "0 5px",
            }}
          >
            &times;
          </button>
        </div>
        <div style={{ padding: "20px" }}>{children}</div>
      </div>
    </div>
  );
};

export default Modal;
