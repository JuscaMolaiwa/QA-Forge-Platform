import React, { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { getTrends } from "../../api/client";

export default function ReportChart() {
  const [data, setData] = useState([]);
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getTrends(days)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [days]);

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <span style={{ fontWeight: 600, fontSize: 15 }}>Daily Trends</span>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          style={{ width: "auto", padding: "6px 10px" }}
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
        </select>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", color: "var(--gray-400)", padding: "2rem" }}>Loading…</div>
      ) : data.length === 0 ? (
        <div style={{ textAlign: "center", color: "var(--gray-400)", padding: "2rem", fontSize: 13 }}>
          No data yet — run some tests first.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data} barGap={2}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8eaed" />
            <XAxis dataKey="day" tick={{ fontSize: 11, fontFamily: "var(--mono)" }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ fontFamily: "var(--sans)", fontSize: 12, borderRadius: 8, border: "1px solid #e8eaed" }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="passed" name="Passed" fill="#1d9e75" radius={[3, 3, 0, 0]} />
            <Bar dataKey="failed" name="Failed" fill="#e24b4a" radius={[3, 3, 0, 0]} />
            <Bar dataKey="error" name="Error" fill="#ef9f27" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
