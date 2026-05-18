import React from "react";

export default function Header({ activeTab, onTabChange, queueDepth }) {
  const tabs = ["Devices", "Test Runner", "Reports"];

  return (
    <header style={{
      background: "#fff",
      borderBottom: "1px solid var(--gray-200)",
      padding: "0 1.5rem",
      display: "flex",
      alignItems: "center",
      gap: "2rem",
      height: 56,
      position: "sticky",
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 20 }}>📱</span>
        <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: "-0.02em" }}>
          Device Farm
        </span>
      </div>

      <nav style={{ display: "flex", gap: 2 }}>
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            style={{
              background: activeTab === tab ? "var(--brand-light)" : "transparent",
              color: activeTab === tab ? "var(--brand)" : "var(--gray-600)",
              border: "none",
              padding: "6px 14px",
              fontWeight: activeTab === tab ? 600 : 400,
              fontSize: 13,
              borderRadius: 6,
              cursor: "pointer",
            }}
          >
            {tab}
          </button>
        ))}
      </nav>

      {queueDepth > 0 && (
        <div style={{
          marginLeft: "auto",
          background: "var(--warning-light)",
          color: "var(--warning)",
          fontFamily: "var(--mono)",
          fontSize: 11,
          padding: "4px 10px",
          borderRadius: 99,
          fontWeight: 500,
        }}>
          ⏳ {queueDepth} queued
        </div>
      )}
    </header>
  );
}
