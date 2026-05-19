import { useState, useEffect, useCallback } from "react";
import { getDevices, syncDevices as apiSync } from "../api/client";

export function useDevices() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
  try {
    setError(null);
    const data = await getDevices();
    setDevices(Array.isArray(data) ? data : (data?.devices ?? [])); 
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
}, []);

  const syncAdb = useCallback(async () => {
    try {
      const result = await apiSync();
      await load();
      return result;
    } catch (err) {
      setError(err.message);
    }
  }, [load]);

  // Update a single device in place (from WebSocket events)
  const updateDevice = useCallback((updated) => {
    setDevices((prev) =>
      prev.map((d) => (d.id === updated.id ? { ...d, ...updated } : d))
    );
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, [load]);

  return { devices, loading, error, reload: load, syncAdb, updateDevice };
}
