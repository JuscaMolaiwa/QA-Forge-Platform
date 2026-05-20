import React, { useState } from "react";
import StatusBadge from "../Dashboard/StatusBadge";

const INITIAL_SHOW = 3;

export default function ResultsViewer({ sessions }) {
  const [selected, setSelected] = useState(null);
  const [showAll, setShowAll] = useState(false);

  const finished = (Array.isArray(sessions) ? sessions : []).filter((s) =>
    ["passed", "failed", "error", "cancelled"].includes(s.status)
  );

  const visible = showAll ? finished : finished.slice(0, INITIAL_SHOW);
  const hasMore = finished.length > INITIAL_SHOW;

  if (finished.length === 0) {
    return (
      <div style={{ color: "var(--gray-400)", textAlign: "center", padding: "2rem", fontSize: 13 }}>
        No completed sessions yet
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: selected ? "1fr 1fr" : "1fr", gap: 12 }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {visible.map((s) => (
          <div
            key={s.session_id}
            className="card"
            onClick={() => setSelected(s.session_id === selected ? null : s.session_id)}
            style={{
              padding: "12px 16px",
              cursor: "pointer",
              borderLeft: `3px solid ${s.status === "passed" ? "var(--brand-mid)" : s.status === "failed" ? "#e24b4a" : "#9aa0a6"}`,
              background: s.session_id === selected ? "var(--gray-50)" : "#fff",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <StatusBadge status={s.status} />
              <span style={{ fontWeight: 500, fontSize: 13, flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {s.test_name}
              </span>
              {s.duration_seconds != null && (
                <span style={{ fontSize: 11, fontFamily: "var(--mono)", color: "var(--gray-400)" }}>
                  {s.duration_seconds.toFixed(1)}s
                </span>
              )}
            </div>
            {s.total_count > 0 && (
              <div style={{ fontSize: 11, color: "var(--gray-600)" }}>
                {s.passed_count} passed · {s.failed_count} failed · {s.total_count} total
              </div>
            )}
          </div>
        ))}

        {/* View more / less toggle */}
        {hasMore && (
          <button
            className="btn-ghost"
            onClick={() => setShowAll((v) => !v)}
            style={{ fontSize: 12, padding: "6px 0", width: "100%", borderRadius: 6 }}
          >
            {showAll
              ? "↑ View less"
              : `↓ View ${finished.length - INITIAL_SHOW} more`}
          </button>
        )}
      </div>

      {selected && (() => {
        const s = sessions.find((x) => x.session_id === selected);
        if (!s) return null;
        return (
          <div className="card" style={{ padding: "1rem", overflow: "auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12, alignItems: "center" }}>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{s.test_name}</span>
              <button className="btn-ghost" style={{ fontSize: 11, padding: "4px 8px" }} onClick={() => setSelected(null)}>✕</button>
            </div>
            {s.error_message && (
              <div className="error-msg" style={{ marginBottom: 10, fontSize: 12 }}>{s.error_message}</div>
            )}
            <pre style={{
              fontFamily: "var(--mono)",
              fontSize: 11,
              background: "#1a1a1a",
              color: "#e8eaed",
              padding: "1rem",
              borderRadius: 6,
              overflow: "auto",
              maxHeight: 420,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}>
              {s.log_output || "(no output)"}
            </pre>
          </div>
        );
      })()}
    </div>
  );
}