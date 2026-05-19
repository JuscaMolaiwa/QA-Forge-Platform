import React, { useState, useEffect } from "react";
import { submitTest } from "../../api/client";

const BLANK = {
  test_name: "",
  test_content: `import pytest
import os
from appium import webdriver
from appium.options import UiAutomator2Options as AppiumOptions

@pytest.fixture(scope="module")
def driver():
    opts = AppiumOptions()
    opts.platform_name = os.environ["PLATFORM_NAME"]
    opts.set_capability("appium:udid", os.environ["DEVICE_UDID"])
    opts.set_capability("appium:app", os.environ.get("APP_PATH", ""))
    opts.set_capability("appium:automationName", "UiAutomator2")
    drv = webdriver.Remote(
        f"http://{os.environ['APPIUM_HOST']}:{os.environ['APPIUM_PORT']}",
        options=opts,
    )
    yield drv
    drv.quit()

def test_app_launches(driver):
    assert driver.current_activity is not None
`,
  app_path: "",
  platform: "android",
};

export default function TestForm({ onSubmitted, prefill }) {
  const [form, setForm] = useState(BLANK);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);
  const [fromLibrary, setFromLibrary] = useState(null);

  useEffect(() => {
    if (!prefill) return;
    const name = prefill.name || "";
    const content = prefill.content || "";
    const platform = prefill.platform || "android";
    setFromLibrary(name);
    setForm({
      test_name: name,
      test_content: content,
      app_path: "",
      platform,
    });
    setSuccess(null);
    setError("");
  }, [prefill]);

  const handleSubmit = async () => {
    setError("");
    setSuccess(null);
    setSubmitting(true);
    try {
      const session = await submitTest(form);
      setSuccess(session);
      if (onSubmitted) onSubmitted(session);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setForm(BLANK);
    setFromLibrary(null);
    setSuccess(null);
    setError("");
  };

  return (
    <div>
      <div style={{ marginBottom: "1.25rem" }}>
        <span style={{ fontWeight: 600, fontSize: 16 }}>Run Test</span>

        {fromLibrary && (
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            background: "var(--brand-light)",
            border: "1px solid var(--brand-soft)",
            borderRadius: 8,
            padding: "10px 14px",
            marginBottom: 4,
            fontSize: 13,
          }}>
            <span style={{ flex: 1, color: "var(--brand)", fontWeight: 500 }}>
              📂 <strong>{fromLibrary}</strong> loaded — review the script below and click <strong>▶ Run Test</strong> to execute
            </span>
            <button
              className="btn-ghost"
              style={{ fontSize: 11, padding: "2px 8px", flexShrink: 0 }}
              onClick={() => setFromLibrary(null)}
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {error && <div className="error-msg" style={{ marginBottom: 12 }}>{error}</div>}

      {success && (
        <div style={{
          background: "var(--brand-light)", color: "var(--brand)",
          border: "1px solid var(--brand-soft)", borderRadius: 6,
          padding: "10px 14px", fontSize: 13, marginBottom: 12,
        }}>
          ✓ Queued — <code style={{ fontFamily: "var(--mono)" }}>{success.session_id}</code>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        <div>
          <label>Test Name *</label>
          <input
            placeholder="e.g. Login smoke test"
            value={form.test_name}
            onChange={(e) => setForm((f) => ({ ...f, test_name: e.target.value }))}
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <label>Platform</label>
            <select value={form.platform} onChange={(e) => setForm((f) => ({ ...f, platform: e.target.value }))}>
              <option value="android">Android</option>
              <option value="ios">iOS</option>
            </select>
          </div>
          <div>
            <label>App Path (optional)</label>
            <input
              placeholder="/path/to/app.apk"
              value={form.app_path}
              onChange={(e) => setForm((f) => ({ ...f, app_path: e.target.value }))}
            />
          </div>
        </div>

        <div>
          <label>Test Script *</label>
          <textarea
            rows={16}
            value={form.test_content}
            onChange={(e) => setForm((f) => ({ ...f, test_content: e.target.value }))}
            spellCheck={false}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <button className="btn-ghost" onClick={handleReset}>Reset</button>
          <button
            className="btn-primary"
            onClick={handleSubmit}
            disabled={submitting || !form.test_name.trim() || !form.test_content.trim()}
          >
            {submitting ? "Submitting…" : "▶ Run Test"}
          </button>
        </div>
      </div>
    </div>
  );
}
