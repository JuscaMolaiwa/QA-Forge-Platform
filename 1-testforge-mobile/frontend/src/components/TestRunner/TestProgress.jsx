import React from "react";
import StatusBadge from "../Dashboard/StatusBadge";

export default function TestProgress({ sessions, onCancel }) {
  const active = sessions.filter((s) => ["queued", "running"].includes(s.status));

  if (active.length === 0) {
    return (
      <div style={{ color: "var(--gray-400)", textAlign: "center", padding: "2rem", fontSize: 13 }}>
        No active sessions
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {active.map((s) => (
        <div
          key={s.session_id}
          className="card"
          style={{ padding: "12px 16px", display: "flex", alignItems: "center", gap: 12 }}
        >
          <StatusBadge status={s.status} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontWeight: 500, fontSize: 13, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {s.test_name}
            </div>
            {s.device_name && (
              <div style={{ fontSize: 11, color: "var(--gray-400)", fontFamily: "var(--mono)" }}>
                {s.device_name} · {s.device_udid}
              </div>
            )}
          </div>
          {s.status === "queued" && (
            <button
              className="btn-danger"
              style={{ fontSize: 11, padding: "4px 10px", flexShrink: 0 }}
              onClick={() => onCancel(s.session_id)}
            >
              Cancel
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
