import React, { useState, useEffect } from "react";
import StatusBadge from "../Dashboard/StatusBadge";

const INITIAL_SHOW = 3;
const API_URL = process.env.REACT_APP_API_URL || "";

export default function ResultsViewer({ sessions }) {
  const [selected, setSelected] = useState(null);
  const [showAll, setShowAll] = useState(false);
  const [screenshots, setScreenshots] = useState([]);
  const [loadingShots, setLoadingShots] = useState(false);
  const [activeShot, setActiveShot] = useState(null);

  const finished = (Array.isArray(sessions) ? sessions : []).filter((s) =>
    ["passed", "failed", "error", "cancelled"].includes(s.status)
  );
  const visible = showAll ? finished : finished.slice(0, INITIAL_SHOW);
  const hasMore = finished.length > INITIAL_SHOW;

  // Load screenshots when a session is selected
  useEffect(() => {
    if (!selected) { setScreenshots([]); setActiveShot(null); return; }
    setLoadingShots(true);
    fetch(`${API_URL}/api/tests/${selected}/screenshots`)
      .then((r) => r.json())
      .then((data) => {
        setScreenshots(Array.isArray(data) ? data : []);
        setActiveShot(Array.isArray(data) && data.length > 0 ? data[data.length - 1] : null);
      })
      .catch(() => setScreenshots([]))
      .finally(() => setLoadingShots(false));
  }, [selected]);

  if (finished.length === 0) {
    return (
      <div style={{ color: "var(--gray-400)", textAlign: "center", padding: "2rem", fontSize: 13 }}>
        No completed sessions yet
      </div>
    );
  }

  const selectedSession = sessions.find((x) => x.session_id === selected);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>

      {/* ── Session list ── */}
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

        {hasMore && (
          <button
            className="btn-ghost"
            onClick={() => setShowAll((v) => !v)}
            style={{ fontSize: 12, padding: "6px 0", width: "100%", borderRadius: 6 }}
          >
            {showAll ? "↑ View less" : `↓ View ${finished.length - INITIAL_SHOW} more`}
          </button>
        )}
      </div>

      {/* ── Detail panel ── */}
      {selected && selectedSession && (
        <div className="card" style={{ padding: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12, alignItems: "center" }}>
            <span style={{ fontWeight: 600, fontSize: 13 }}>{selectedSession.test_name}</span>
            <button className="btn-ghost" style={{ fontSize: 11, padding: "4px 8px" }} onClick={() => setSelected(null)}>✕</button>
          </div>

          {selectedSession.error_message && (
            <div className="error-msg" style={{ marginBottom: 10, fontSize: 12 }}>{selectedSession.error_message}</div>
          )}

          {/* Screenshots */}
          {loadingShots ? (
            <div style={{ fontSize: 12, color: "var(--gray-400)", marginBottom: 10 }}>Loading screenshots…</div>
          ) : screenshots.length > 0 ? (
            <div style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, fontWeight: 500, color: "var(--gray-600)", marginBottom: 6, fontFamily: "var(--mono)" }}>
                SCREENSHOTS ({screenshots.length})
              </div>

              {/* Main preview */}
              {activeShot && (
                <img
                  src={activeShot.data}
                  alt={activeShot.name}
                  style={{
                    width: "100%", borderRadius: 6, border: "1px solid var(--gray-200)",
                    marginBottom: 8, objectFit: "contain", maxHeight: 320,
                    background: "#1a1a1a",
                  }}
                />
              )}

              {/* Thumbnail strip */}
              <div style={{ display: "flex", gap: 6, overflowX: "auto", paddingBottom: 4 }}>
                {screenshots.map((shot, i) => (
                  <img
                    key={i}
                    src={shot.data}
                    alt={shot.name}
                    onClick={() => setActiveShot(shot)}
                    style={{
                      width: 64, height: 48, objectFit: "cover",
                      borderRadius: 4, cursor: "pointer", flexShrink: 0,
                      border: `2px solid ${activeShot?.name === shot.name ? "var(--brand-mid)" : "var(--gray-200)"}`,
                    }}
                  />
                ))}
              </div>
            </div>
          ) : (
            <div style={{ fontSize: 12, color: "var(--gray-400)", marginBottom: 10 }}>
              No screenshots captured
            </div>
          )}

          {/* Log output */}
          <div style={{ fontSize: 12, fontWeight: 500, color: "var(--gray-600)", marginBottom: 6, fontFamily: "var(--mono)" }}>
            LOG OUTPUT
          </div>
          <pre style={{
            fontFamily: "var(--mono)", fontSize: 11,
            background: "#1a1a1a", color: "#e8eaed",
            padding: "1rem", borderRadius: 6,
            overflow: "auto", maxHeight: 320,
            whiteSpace: "pre-wrap", wordBreak: "break-word",
          }}>
            {selectedSession.log_output || "(no output)"}
          </pre>
        </div>
      )}
    </div>
  );
}