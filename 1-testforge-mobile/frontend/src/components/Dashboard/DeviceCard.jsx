import React from "react";
import StatusBadge from "./StatusBadge";
import { deleteDevice } from "../../api/client";

export default function DeviceCard({ device, onDeleted }) {
  const handleDelete = async () => {
    if (!window.confirm(`Remove device ${device.name}?`)) return;
    try {
      await deleteDevice(device.id);
      onDeleted(device.id);
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div
      className="card"
      style={{
        padding: "1rem 1.25rem",
        display: "flex",
        flexDirection: "column",
        gap: 10,
        borderLeft: `3px solid ${device.status === "online" ? "var(--brand-mid)" : device.status === "busy" ? "#ef9f27" : "#9aa0a6"}`,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 2 }}>{device.name}</div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--gray-600)" }}>
            {device.udid}
          </div>
        </div>
        <StatusBadge status={device.status} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px 12px" }}>
        <Prop label="Platform" value={device.platform} />
        <Prop label="Version" value={device.platform_version || "—"} />
        <Prop label="Model" value={device.model || "—"} />
        <Prop label="Type" value={device.is_cloud ? `Cloud (${device.cloud_provider || "?"})` : "Local"} />
        {device.appium_port && <Prop label="Appium Port" value={device.appium_port} />}
      </div>

      {device.last_seen && (
        <div style={{ fontSize: 11, color: "var(--gray-400)", fontFamily: "var(--mono)" }}>
          Last seen {new Date(device.last_seen).toLocaleString()}
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <button className="btn-danger" style={{ fontSize: 12, padding: "5px 10px" }} onClick={handleDelete}>
          Remove
        </button>
      </div>
    </div>
  );
}

function Prop({ label, value }) {
  return (
    <div>
      <div style={{ fontSize: 10, fontFamily: "var(--mono)", color: "var(--gray-400)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
        {label}
      </div>
      <div style={{ fontSize: 13, fontWeight: 500 }}>{value}</div>
    </div>
  );
}
