import React, { useEffect, useState } from "react";
import StatusBadge from "../Dashboard/StatusBadge";
import { getHistory } from "../../api/client";

export default function SessionHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHistory(30)
      .then(setHistory)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ color: "var(--gray-400)", padding: "1rem", fontSize: 13 }}>Loading…</div>;
  if (history.length === 0) return <div style={{ color: "var(--gray-400)", padding: "1rem", fontSize: 13 }}>No history yet.</div>;

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: "1px solid var(--gray-200)" }}>
            {["Test", "Device", "Status", "Duration", "Passed", "Failed", "Finished"].map((h) => (
              <th key={h} style={{ textAlign: "left", padding: "8px 10px", fontSize: 11, fontFamily: "var(--mono)", color: "var(--gray-400)", fontWeight: 500, whiteSpace: "nowrap" }}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {history.map((s) => (
            <tr key={s.session_id} style={{ borderBottom: "1px solid var(--gray-100)" }}>
              <td style={{ padding: "9px 10px", fontWeight: 500, maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {s.test_name}
              </td>
              <td style={{ padding: "9px 10px", fontFamily: "var(--mono)", fontSize: 11, color: "var(--gray-600)" }}>
                {s.device_name || "—"}
              </td>
              <td style={{ padding: "9px 10px" }}>
                <StatusBadge status={s.status} />
              </td>
              <td style={{ padding: "9px 10px", fontFamily: "var(--mono)", fontSize: 12, color: "var(--gray-600)" }}>
                {s.duration_seconds != null ? `${s.duration_seconds.toFixed(1)}s` : "—"}
              </td>
              <td style={{ padding: "9px 10px", color: "var(--brand)", fontWeight: 500 }}>{s.passed_count}</td>
              <td style={{ padding: "9px 10px", color: s.failed_count > 0 ? "var(--danger)" : "var(--gray-400)", fontWeight: s.failed_count > 0 ? 600 : 400 }}>
                {s.failed_count}
              </td>
              <td style={{ padding: "9px 10px", fontSize: 11, fontFamily: "var(--mono)", color: "var(--gray-400)", whiteSpace: "nowrap" }}>
                {s.finished_at ? new Date(s.finished_at).toLocaleString() : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
