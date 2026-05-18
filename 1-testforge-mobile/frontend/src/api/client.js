const BASE = process.env.REACT_APP_API_URL || "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// Devices
export const getDevices = () => request("/api/devices/");
export const syncDevices = () => request("/api/devices/sync", { method: "POST" });
export const registerDevice = (payload) =>
  request("/api/devices/", { method: "POST", body: JSON.stringify(payload) });
export const deleteDevice = (id) =>
  request(`/api/devices/${id}`, { method: "DELETE" });

// Tests
export const getSessions = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/api/tests/${qs ? "?" + qs : ""}`);
};
export const getSession = (id) => request(`/api/tests/${id}`);
export const submitTest = (payload) =>
  request("/api/tests/", { method: "POST", body: JSON.stringify(payload) });
export const cancelSession = (id) =>
  request(`/api/tests/${id}`, { method: "DELETE" });
export const getQueueStatus = () => request("/api/tests/queue/status");

// Reports
export const getSummary = () => request("/api/reports/summary");
export const getHistory = (limit = 30) => request(`/api/reports/history?limit=${limit}`);
export const getTrends = (days = 7) => request(`/api/reports/trends?days=${days}`);
