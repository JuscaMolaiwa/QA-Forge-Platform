import React, { useState, useEffect, useCallback } from "react";
import {
  getLibrary,
  getLibraryScript,
  createLibraryScript,
  updateLibraryScript,
  deleteLibraryScript,
  uploadLibraryScript,
} from "../../api/client";

const PLATFORM_COLORS = {
  android: { bg: "#e6f1fb", color: "#185fa5" },
  ios: { bg: "#f3eefb", color: "#6b34ac" },
};

export default function TestLibrary({ onSelect }) {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [selected, setSelected] = useState(null);    // script being previewed
  const [editing, setEditing] = useState(null);      // script being edited
  const [showNew, setShowNew] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await getLibrary();
      setScripts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const loadFull = async (id) => {
    try {
      const full = await getLibraryScript(id);
      setSelected(full);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    try {
      await deleteLibraryScript(id);
      setScripts((prev) => prev.filter((s) => s.id !== id));
      if (selected?.id === id) setSelected(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const script = await uploadLibraryScript(file);
      setScripts((prev) => [script, ...prev]);
    } catch (err) {
      setError(err.message);
    }
    e.target.value = "";
  };

  const filtered = scripts.filter((s) => {
    const matchSearch = s.name.toLowerCase().includes(search.toLowerCase()) ||
      (s.description || "").toLowerCase().includes(search.toLowerCase());
    const matchPlatform = platformFilter === "all" || s.platform === platformFilter;
    return matchSearch && matchPlatform;
  });

  return (
    <div style={{ display: "grid", gridTemplateColumns: selected ? "300px 1fr" : "1fr", gap: 12, height: "100%" }}>

      {/* ── Left: script list ── */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>

        {/* Toolbar */}
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          <input
            placeholder="Search tests…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ flex: 1, minWidth: 120 }}
          />
          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            style={{ width: "auto", padding: "8px 10px" }}
          >
            <option value="all">All platforms</option>
            <option value="android">Android</option>
            <option value="ios">iOS</option>
          </select>
        </div>

        <div style={{ display: "flex", gap: 6 }}>
          <button className="btn-primary" style={{ flex: 1, fontSize: 12 }} onClick={() => { setShowNew(true); setEditing(null); setSelected(null); }}>
            + New Script
          </button>
          <label style={{
            flex: 1, textAlign: "center", cursor: "pointer",
            background: "transparent", border: "1px solid var(--gray-200)",
            borderRadius: 6, padding: "7px 10px", fontSize: 12,
            color: "var(--gray-600)", fontWeight: 500, marginBottom: 0,
          }}>
            ↑ Upload .py
            <input type="file" accept=".py" style={{ display: "none" }} onChange={handleUpload} />
          </label>
        </div>

        {error && <div className="error-msg" style={{ fontSize: 12 }}>{error}</div>}

        {loading ? (
          <div style={{ color: "var(--gray-400)", fontSize: 13, padding: "1rem 0" }}>Loading…</div>
        ) : filtered.length === 0 ? (
          <div style={{ color: "var(--gray-400)", fontSize: 13, padding: "1rem 0", textAlign: "center" }}>
            {scripts.length === 0 ? "No scripts yet — create one or upload a .py file." : "No matches."}
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 6, overflowY: "auto", maxHeight: 480 }}>
            {filtered.map((s) => (
              <ScriptRow
                key={s.id}
                script={s}
                isSelected={selected?.id === s.id}
                onClick={() => selected?.id === s.id ? setSelected(null) : loadFull(s.id)}
                onRun={async () => {
                  try {
                    const full = await getLibraryScript(s.id);
                    onSelect(full);
                  } catch (err) {
                    setError(err.message);
                  }
                }}
                onEdit={() => { loadFull(s.id).then(() => setEditing(s)); setShowNew(false); }}
                onDelete={() => handleDelete(s.id, s.name)}
              />
            ))}
          </div>
        )}
      </div>

      {/* ── Right: preview / editor ── */}
      {(selected || showNew) && (
        <div>
          {showNew && (
            <NewScriptForm
              onSaved={(script) => {
                setScripts((prev) => [script, ...prev]);
                setShowNew(false);
                setSelected(script);
              }}
              onCancel={() => setShowNew(false)}
            />
          )}
          {selected && !showNew && (
            editing?.id === selected.id ? (
              <EditScriptForm
                script={selected}
                onSaved={(updated) => {
                  setScripts((prev) => prev.map((s) => s.id === updated.id ? updated : s));
                  setSelected(updated);
                  setEditing(null);
                }}
                onCancel={() => setEditing(null)}
              />
            ) : (
              <ScriptPreview
                script={selected}
                onRun={() => onSelect(selected)}
                onEdit={() => setEditing(selected)}
                onClose={() => setSelected(null)}
              />
            )
          )}
        </div>
      )}
    </div>
  );
}

// ── Sub-components ─────────────────────────────────────────────────────────

function ScriptRow({ script, isSelected, onClick, onRun, onEdit, onDelete }) {
  const pc = PLATFORM_COLORS[script.platform] || PLATFORM_COLORS.android;
  return (
    <div
      className="card"
      onClick={onClick}
      style={{
        padding: "10px 12px",
        cursor: "pointer",
        borderLeft: `3px solid ${isSelected ? "var(--brand-mid)" : "transparent"}`,
        background: isSelected ? "var(--brand-light)" : "#fff",
        transition: "background 0.1s",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
        <span style={{ fontWeight: 500, fontSize: 13, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {script.name}
        </span>
        <span style={{ fontSize: 10, fontFamily: "var(--mono)", background: pc.bg, color: pc.color, padding: "2px 6px", borderRadius: 99, flexShrink: 0 }}>
          {script.platform}
        </span>
      </div>
      {script.description && (
        <div style={{ fontSize: 11, color: "var(--gray-400)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginBottom: 6 }}>
          {script.description}
        </div>
      )}
      <div style={{ display: "flex", gap: 5, justifyContent: "flex-end" }} onClick={(e) => e.stopPropagation()}>
        {/* <button className="btn-primary" style={{ fontSize: 11, padding: "3px 10px" }} onClick={onRun}>▶ Run</button> */}
        <button className="btn-ghost" style={{ fontSize: 11, padding: "3px 10px" }} onClick={onRun}>↓ Load</button>
        <button className="btn-ghost" style={{ fontSize: 11, padding: "3px 8px" }} onClick={onEdit}>Edit</button>
        <button className="btn-danger" style={{ fontSize: 11, padding: "3px 8px" }} onClick={onDelete}>✕</button>
      </div>
    </div>
  );
}

function ScriptPreview({ script, onRun, onEdit, onClose }) {
  return (
    <div className="card" style={{ padding: "1.25rem", height: "100%" }}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 12 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600, fontSize: 15 }}>{script.name}</div>
          <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--gray-400)" }}>{script.filename}</div>
        </div>
        <button className="btn-ghost" style={{ fontSize: 11, padding: "4px 8px" }} onClick={onClose}>✕</button>
      </div>
      {script.description && (
        <div style={{ fontSize: 13, color: "var(--gray-600)", marginBottom: 12 }}>{script.description}</div>
      )}
      {script.tags?.length > 0 && (
        <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: 12 }}>
          {script.tags.map((t) => (
            <span key={t} style={{ fontSize: 11, fontFamily: "var(--mono)", background: "var(--gray-100)", color: "var(--gray-600)", padding: "2px 8px", borderRadius: 99 }}>{t}</span>
          ))}
        </div>
      )}
      <pre style={{
        fontFamily: "var(--mono)", fontSize: 11,
        background: "#1a1a1a", color: "#e8eaed",
        padding: "1rem", borderRadius: 6,
        overflow: "auto", maxHeight: 340,
        whiteSpace: "pre-wrap", wordBreak: "break-word",
        marginBottom: 12,
      }}>
        {script.content}
      </pre>
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button className="btn-ghost" onClick={onEdit}>Edit</button>
        {/* <button className="btn-primary" onClick={onRun}>▶ Run This Test</button> */}
        <button className="btn-primary" onClick={onRun}>↓ Load into Runner</button>
      </div>
    </div>
  );
}

function NewScriptForm({ onSaved, onCancel }) {
  const [form, setForm] = useState({ name: "", description: "", platform: "android", tags: "", content: "import pytest\n\ndef test_example():\n    assert True\n" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSave = async () => {
    setError(""); setSaving(true);
    try {
      const script = await createLibraryScript({ ...form, tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean) });
      onSaved(script);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return <ScriptForm title="New Script" form={form} setForm={setForm} saving={saving} error={error} onSave={handleSave} onCancel={onCancel} saveLabel="Save to Library" />;
}

function EditScriptForm({ script, onSaved, onCancel }) {
  const [form, setForm] = useState({
    name: script.name,
    description: script.description || "",
    platform: script.platform,
    tags: (script.tags || []).join(", "),
    content: script.content,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSave = async () => {
    setError(""); setSaving(true);
    try {
      const updated = await updateLibraryScript(script.id, { ...form, tags: form.tags.split(",").map((t) => t.trim()).filter(Boolean) });
      onSaved(updated);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return <ScriptForm title={`Edit — ${script.name}`} form={form} setForm={setForm} saving={saving} error={error} onSave={handleSave} onCancel={onCancel} saveLabel="Save Changes" />;
}

function ScriptForm({ title, form, setForm, saving, error, onSave, onCancel, saveLabel }) {
  const f = (key) => ({ value: form[key], onChange: (e) => setForm((p) => ({ ...p, [key]: e.target.value })) });
  return (
    <div className="card" style={{ padding: "1.25rem" }}>
      <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 14 }}>{title}</div>
      {error && <div className="error-msg" style={{ marginBottom: 10, fontSize: 12 }}>{error}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
          <div><label>Name *</label><input placeholder="Login Smoke Test" {...f("name")} /></div>
          <div>
            <label>Platform</label>
            <select {...f("platform")}>
              <option value="android">Android</option>
              <option value="ios">iOS</option>
            </select>
          </div>
        </div>
        <div><label>Description</label><input placeholder="What does this test verify?" {...f("description")} /></div>
        <div><label>Tags (comma-separated)</label><input placeholder="smoke, login, auth" {...f("tags")} /></div>
        <div>
          <label>Script *</label>
          <textarea rows={16} spellCheck={false} {...f("content")} />
        </div>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button className="btn-ghost" onClick={onCancel}>Cancel</button>
          <button className="btn-primary" onClick={onSave} disabled={saving || !form.name.trim() || !form.content.trim()}>
            {saving ? "Saving…" : saveLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
