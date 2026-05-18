import React, { useState } from "react";
import DeviceCard from "./DeviceCard";
import { registerDevice } from "../../api/client";

export default function DeviceGrid({ devices, loading, error, onSync, onDeleted }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ udid: "", name: "", platform: "android", platform_version: "", model: "" });
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const handleSubmit = async () => {
    setFormError("");
    setSubmitting(true);
    try {
      await registerDevice(form);
      setShowForm(false);
      setForm({ udid: "", name: "", platform: "android", platform_version: "", model: "" });
      onSync();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const counts = {
    online: devices.filter((d) => d.status === "online").length,
    busy: devices.filter((d) => d.status === "busy").length,
    offline: devices.filter((d) => d.status === "offline").length,
  };

  return (
    <div>
      {/* Stats row */}
      <div style={{ display: "flex", gap: 10, marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {[
          { label: "Online", value: counts.online, color: "var(--brand)" },
          { label: "Busy", value: counts.busy, color: "#854f0b" },
          { label: "Offline", value: counts.offline, color: "var(--gray-400)" },
          { label: "Total", value: devices.length, color: "var(--accent)" },
        ].map(({ label, value, color }) => (
          <div key={label} className="card" style={{ flex: 1, minWidth: 100, padding: "14px 18px" }}>
            <div style={{ fontSize: 11, fontFamily: "var(--mono)", color: "var(--gray-400)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 26, fontWeight: 600, color }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div style={{ display: "flex", gap: 8, marginBottom: "1rem", alignItems: "center" }}>
        <span style={{ fontSize: 13, fontWeight: 600, flex: 1, color: "var(--gray-900)" }}>
          Devices ({devices.length})
        </span>
        <button className="btn-ghost" onClick={onSync}>↻ Sync ADB</button>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancel" : "+ Register"}
        </button>
      </div>

      {/* Register form */}
      {showForm && (
        <div className="card" style={{ padding: "1.25rem", marginBottom: "1rem" }}>
          <div style={{ fontWeight: 600, marginBottom: 12 }}>Register Device</div>
          {formError && <div className="error-msg" style={{ marginBottom: 10 }}>{formError}</div>}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
            {[
              { key: "udid", label: "UDID *" },
              { key: "name", label: "Name *" },
              { key: "platform_version", label: "OS Version" },
              { key: "model", label: "Model" },
            ].map(({ key, label }) => (
              <div key={key}>
                <label>{label}</label>
                <input
                  value={form[key]}
                  onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                />
              </div>
            ))}
            <div>
              <label>Platform *</label>
              <select value={form.platform} onChange={(e) => setForm((f) => ({ ...f, platform: e.target.value }))}>
                <option value="android">Android</option>
                <option value="ios">iOS</option>
              </select>
            </div>
          </div>
          <div style={{ marginTop: 12, display: "flex", justifyContent: "flex-end", gap: 8 }}>
            <button className="btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleSubmit} disabled={submitting}>
              {submitting ? "Registering..." : "Register"}
            </button>
          </div>
        </div>
      )}

      {error && <div className="error-msg" style={{ marginBottom: "1rem" }}>{error}</div>}

      {loading ? (
        <div style={{ textAlign: "center", color: "var(--gray-400)", padding: "3rem" }}>Loading devices…</div>
      ) : devices.length === 0 ? (
        <div className="card" style={{ padding: "3rem", textAlign: "center", color: "var(--gray-400)" }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📱</div>
          <div>No devices found. Connect a device via USB or click Sync ADB.</div>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
          {devices.map((d) => (
            <DeviceCard key={d.id} device={d} onDeleted={onDeleted} />
          ))}
        </div>
      )}
    </div>
  );
}
