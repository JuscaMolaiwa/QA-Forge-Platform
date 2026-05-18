import React, { useState } from "react";
import { submitTest } from "../../api/client";

const SAMPLE = `# Paste your Appium pytest test here
# Environment variables are injected automatically:
#   APPIUM_HOST, APPIUM_PORT, DEVICE_UDID, PLATFORM_NAME, APP_PATH

import pytest
from appium import webdriver
from appium.options import AppiumOptions
import os

@pytest.fixture(scope="module")
def driver():
    opts = AppiumOptions()
    opts.platform_name = os.environ["PLATFORM_NAME"]
    opts.udid = os.environ["DEVICE_UDID"]
    opts.app = os.environ.get("APP_PATH", "")
    url = f"http://{os.environ['APPIUM_HOST']}:{os.environ['APPIUM_PORT']}"
    drv = webdriver.Remote(url, options=opts)
    yield drv
    drv.quit()

def test_app_launches(driver):
    assert driver.current_activity is not None
`;

export default function TestForm({ onSubmitted }) {
  const [form, setForm] = useState({
    test_name: "",
    test_content: SAMPLE,
    app_path: "",
    platform: "android",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);

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

  return (
    <div>
      <div style={{ fontWeight: 600, fontSize: 16, marginBottom: "1.25rem" }}>Submit Test</div>

      {error && <div className="error-msg" style={{ marginBottom: 12 }}>{error}</div>}

      {success && (
        <div style={{ background: "var(--brand-light)", color: "var(--brand)", border: "1px solid var(--brand-soft)", borderRadius: 6, padding: "10px 14px", fontSize: 13, marginBottom: 12 }}>
          ✓ Queued — session ID: <code style={{ fontFamily: "var(--mono)" }}>{success.session_id}</code>
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
            rows={18}
            value={form.test_content}
            onChange={(e) => setForm((f) => ({ ...f, test_content: e.target.value }))}
            spellCheck={false}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
          <button
            className="btn-ghost"
            onClick={() => setForm((f) => ({ ...f, test_name: "", test_content: SAMPLE, app_path: "" }))}
          >
            Reset
          </button>
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
