import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "primary" | "success" | "warning" | "info" | "neutral";
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = "neutral" }) => {
  const styles: Record<string, { bg: string; color: string; border: string }> = {
    primary: { bg: "rgba(0, 123, 255, 0.18)", color: "#66b0ff", border: "1px solid rgba(0, 123, 255, 0.4)" },
    success: { bg: "rgba(40, 167, 69, 0.18)", color: "#5dd879", border: "1px solid rgba(40, 167, 69, 0.4)" },
    warning: { bg: "rgba(255, 193, 7, 0.18)", color: "#ffd54f", border: "1px solid rgba(255, 193, 7, 0.4)" },
    info: { bg: "rgba(23, 162, 184, 0.18)", color: "#4dd0e1", border: "1px solid rgba(23, 162, 184, 0.4)" },
    neutral: { bg: "var(--code-bg, #1f2028)", color: "var(--text, #9ca3af)", border: "1px solid var(--border, #2e303a)" },
  };

  const current = styles[variant] || styles.neutral;

  return (
    <span
      style={{
        display: "inline-block",
        padding: "3px 8px",
        borderRadius: "4px",
        fontSize: "0.8rem",
        fontWeight: 600,
        backgroundColor: current.bg,
        color: current.color,
        border: current.border,
        fontFamily: "sans-serif",
      }}
    >
      {children}
    </span>
  );
};

export default Badge;
