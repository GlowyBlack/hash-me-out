"use client";

import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export default function RequestStatsPage() {
  const [stats, setStats] = useState([]);
  const [order, setOrder] = useState("desc");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const fetchStats = async () => {
    if (!token) {
      setError("You must be logged in as an admin.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await axios.get(`${API_BASE}/requests/stats`, {
        params: { order },
        headers,
      });
      console.log("stats response:", res.data);
      setStats(res.data);
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Failed to load request statistics.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [order]);

  const handleAccept = async (row) => {
    const requestId = row.RequestID ?? row.request_id;
    console.log("ACCEPT clicked for row:", row, "requestId:", requestId);

    try {
      await axios.post(
        `${API_BASE}/requests/${requestId}/accept`,
        {},
        { headers }
      );
      await fetchStats();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to accept requests for this ISBN."
      );
    }
  };

  const handleDecline = async (row) => {
    const requestId = row.RequestID ?? row.request_id;
    console.log("DECLINE clicked for row:", row, "requestId:", requestId);

    try {
      await axios.post(
        `${API_BASE}/requests/${requestId}/decline`,
        {},
        { headers }
      );
      await fetchStats();
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Failed to decline requests for this ISBN."
      );
    }
  };

  const toggleOrder = () => {
    setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
  };

  return (
    <div className="min-h-screen bg-[#F7F9FC] px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-[#14213D]">Book Requests</h1>
        <button
          onClick={toggleOrder}
          className="px-4 py-2 rounded-xl bg-[#FFD52E] text-[#14213D] font-semibold shadow-sm"
        >
          Sort: {order === "asc" ? "Ascending" : "Descending"}
        </button>
      </div>

      {error && (
        <p className="mb-4 text-sm text-red-600">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-[#526187]">Loading...</p>
      ) : (
        <div className="space-y-3">
          {stats.length === 0 ? (
            <p className="text-sm text-[#526187]">No requests found.</p>
          ) : (
            stats.map((row, idx) => {
              const isbn = row.ISBN || row.isbn;
              const total = row["Total Requested"] ?? row.total_requested;

              return (
                <div
                  key={idx}
                  className="bg-white rounded-2xl border border-[#E4ECFF] shadow-sm px-5 py-4 flex items-center justify-between"
                >
                  <div>
                    <p className="text-sm font-semibold text-[#14213D]">
                      ISBN: {isbn}
                    </p>
                    <p className="text-xs text-[#74819A] mt-1">
                      Total requested: {total}
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAccept(row)}
                      className="px-3 py-1.5 rounded-lg bg-emerald-500 text-white text-xs font-semibold"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => handleDecline(row)}
                      className="px-3 py-1.5 rounded-lg bg-red-500 text-white text-xs font-semibold"
                    >
                      Decline
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
