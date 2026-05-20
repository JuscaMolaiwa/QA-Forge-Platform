import React, { useState } from "react";
import StatusBadge from "../Dashboard/StatusBadge";

const INITIAL_SHOW = 3;

export default function TestProgress({ sessions, onCancel }) {
  const [showAll, setShowAll] = useState(false);

  const active = (Array.isArray(sessions) ? sessions : []).filter((s) =>
    ["queued", "running"].includes(s.status)
  );

  const visible = showAll ? active : active.slice(0, INITIAL_SHOW);
  const hasMore = active.length > INITIAL_SHOW;

  if (active.length === 0) {
    return (
      <div style={{ color: "var(--gray-400)", textAlign: "center", padding: "2rem", fontSize: 13 }}>
        No active sessions
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {visible.map((s) => (
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

      {hasMore && (
        <button
          className="btn-ghost"
          onClick={() => setShowAll((v) => !v)}
          style={{ fontSize: 12, padding: "6px 0", width: "100%", borderRadius: 6 }}
        >
          {showAll ? "↑ View less" : `↓ View ${active.length - INITIAL_SHOW} more`}
        </button>
      )}
    </div>
  );
}