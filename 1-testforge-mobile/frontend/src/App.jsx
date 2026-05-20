import React, { useState, useEffect, useCallback } from "react";
import "./styles/theme.css";
import Header from "./components/Common/Header";
import DeviceGrid from "./components/Dashboard/DeviceGrid";
import TestForm from "./components/TestRunner/TestForm";
import TestProgress from "./components/TestRunner/TestProgress";
import ResultsViewer from "./components/TestRunner/ResultsViewer";
import TestLibrary from "./components/TestRunner/TestLibrary";
import ReportChart from "./components/Reports/ReportChart";
import SessionHistory from "./components/Reports/SessionHistory";
import { useDevices } from "./hooks/useDevices";
import { useWebSocket } from "./hooks/useWebSocket";
import { getSessions, cancelSession, getQueueStatus, getSummary } from "./api/client";

export default function App() {
  const [activeTab, setActiveTab] = useState("Devices");
  const [sessions, setSessions] = useState([]);
  const [queueDepth, setQueueDepth] = useState(0);
  const [summary, setSummary] = useState(null);
  const [prefill, setPrefill] = useState(null);

  const { devices, loading, error, reload, syncAdb } = useDevices();

  const handleDeleteDevice = useCallback((id) => {
    reload();
  }, [reload]);

  // WebSocket live updates
  const handleSessionUpdate = useCallback((updated) => {
    setSessions((prev) => {
      const idx = prev.findIndex((s) => s.session_id === updated.session_id);
      if (idx === -1) return [updated, ...prev];
      const next = [...prev];
      next[idx] = updated;
      return next;
    });
  }, []);

  useWebSocket(handleSessionUpdate);

  // Load sessions on mount and periodically
  useEffect(() => {
    const load = async () => {
      try {
        const [s, q, sum] = await Promise.all([
          getSessions({ limit: 100 }),
          getQueueStatus(),
          getSummary(),
        ]);
        setSessions(s);
        setQueueDepth(q.depth);
        setSummary(sum);
      } catch (_) {}
    };
    load();
    const id = setInterval(load, 8000);
    return () => clearInterval(id);
  }, []);

  const handleCancel = async (session_id) => {
    try {
      await cancelSession(session_id);
      setSessions((prev) =>
        prev.map((s) => s.session_id === session_id ? { ...s, status: "cancelled" } : s)
      );
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--gray-100)" }}>
      <Header activeTab={activeTab} onTabChange={setActiveTab} queueDepth={queueDepth} />

      <main style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem 1.5rem" }}>

        {activeTab === "Devices" && (
          <DeviceGrid
            devices={devices}
            loading={loading}
            error={error}
            onSync={syncAdb}
            onReload={reload}
            onDeleted={handleDeleteDevice}
          />
        )}

        {activeTab === "Test Runner" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {/* Library browser — full width */}
            <div className="card" style={{ padding: "1.5rem" }}>
              <div style={{ fontWeight: 600, fontSize: 15, marginBottom: "1rem" }}>
                📂 Test Library
              </div>
              <TestLibrary
                onSelect={(script) => {
                  setPrefill({ ...script, _ts: Date.now() }); // force useEffect re-run
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              />
            </div>

            {/* Runner + active sessions */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
              <div className="card" style={{ padding: "1.5rem" }}>
                <TestForm
                  prefill={prefill}
                  onSubmitted={(s) => setSessions((prev) => [s, ...prev])}
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <div className="card" style={{ padding: "1.25rem" }}>
                  <div style={{ fontWeight: 600, marginBottom: 12 }}>
                    Active ({sessions.filter((s) => ["queued", "running"].includes(s.status)).length})
                  </div>
                  <TestProgress sessions={sessions} onCancel={handleCancel} />
                </div>
                <div className="card" style={{ padding: "1.25rem" }}>
                  <div style={{ fontWeight: 600, marginBottom: 12 }}>Results</div>
                  <ResultsViewer sessions={sessions} />
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "Reports" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
            {summary && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: 10 }}>
                {[
                  { label: "Total Runs", value: summary.total, color: "var(--accent)" },
                  { label: "Pass Rate", value: `${summary.pass_rate}%`, color: "var(--brand)" },
                  { label: "Passed", value: summary.passed, color: "var(--brand)" },
                  { label: "Failed", value: summary.failed, color: "var(--danger)" },
                  { label: "Errors", value: summary.error, color: "#854f0b" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="card" style={{ padding: "14px 18px" }}>
                    <div style={{ fontSize: 10, fontFamily: "var(--mono)", color: "var(--gray-400)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{label}</div>
                    <div style={{ fontSize: 24, fontWeight: 700, color }}>{value}</div>
                  </div>
                ))}
              </div>
            )}
            <div className="card" style={{ padding: "1.5rem" }}>
              <ReportChart />
            </div>
            <div className="card" style={{ padding: "1.5rem" }}>
              <div style={{ fontWeight: 600, marginBottom: 14 }}>Session History</div>
              <SessionHistory />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
