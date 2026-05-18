import React from "react";

const STATUS_STYLES = {
  online:    { bg: "#e1f5ee", color: "#0f6e56", dot: "#1d9e75" },
  offline:   { bg: "#f1f3f4", color: "#5f6368", dot: "#9aa0a6" },
  busy:      { bg: "#faeeda", color: "#854f0b", dot: "#ef9f27" },
  error:     { bg: "#fcebeb", color: "#a32d2d", dot: "#e24b4a" },
  queued:    { bg: "#e6f1fb", color: "#185fa5", dot: "#378add" },
  running:   { bg: "#faeeda", color: "#854f0b", dot: "#ef9f27" },
  passed:    { bg: "#e1f5ee", color: "#0f6e56", dot: "#1d9e75" },
  failed:    { bg: "#fcebeb", color: "#a32d2d", dot: "#e24b4a" },
  cancelled: { bg: "#f1f3f4", color: "#5f6368", dot: "#9aa0a6" },
};

export default function StatusBadge({ status }) {
  const s = STATUS_STYLES[status] || STATUS_STYLES.offline;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 5,
        background: s.bg,
        color: s.color,
        fontSize: 11,
        fontWeight: 500,
        fontFamily: "var(--mono)",
        padding: "3px 8px",
        borderRadius: 99,
        textTransform: "uppercase",
        letterSpacing: "0.05em",
        whiteSpace: "nowrap",
      }}
    >
      <span
        style={{
          width: 6, height: 6, borderRadius: "50%",
          background: s.dot,
          flexShrink: 0,
          animation: status === "running" ? "pulse 1.2s infinite" : "none",
        }}
      />
      {status}
      <style>{`
        @keyframes pulse {
          0%,100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </span>
  );
}
