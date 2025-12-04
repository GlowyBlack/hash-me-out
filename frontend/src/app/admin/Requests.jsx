"use client";

import { useEffect, useState } from "react";
import axios from "axios";

export default function RequestsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // --- Auth Header ---
  const getAuthConfig = () => {
    if (typeof window === "undefined") return {};
    const token = localStorage.getItem("access_token");
    if (!token) return {};
    return {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
  };

  // --- Load Requests ---
  const load = async () => {
    try {
      setLoading(true);
      setError("");

      const config = getAuthConfig();
      if (!config.headers) {
        setError("You must be logged in as an admin to view requests.");
        setRequests([]);
        return;
      }

      const res = await axios.get(
        "http://localhost:8000/requests",
        config
      );

      console.log("Requests from API:", res.data);

      // Normalize keys
      const normalized = res.data.map((r) => ({
        ...r,
        request_id: r.request_id ?? r.id, // support both formats
      }));

      setRequests(normalized);
    } catch (err) {
      console.error("Error loading requests:", err);
      setError("Failed to load requests.");
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  // --- Accept Request ---
  const accept = async (request_id) => {
    try {
      if (!request_id) {
        alert("Missing request_id — cannot accept.");
        return;
      }

      const config = getAuthConfig();

      await axios.post(
        `http://localhost:8000/requests/${request_id}/accept`,
        {},
        config
      );

      await load();
    } catch (err) {
      console.error("Error accepting request:", err);
      alert(err.response?.data?.detail || "Error accepting request.");
    }
  };

  // --- Delete Request ---
  const remove = async (request_id) => {
    try {
      if (!request_id) {
        alert("Missing request_id — cannot delete.");
        return;
      }

      const config = getAuthConfig();

      await axios.delete(
        `http://localhost:8000/requests/${request_id}`,
        config
      );

      await load();
    } catch (err) {
      console.error("Error deleting request:", err);
      alert(err.response?.data?.detail || "Error deleting request.");
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold mb-4">Book Requests</h1>

      {loading && <p>Loading requests...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && requests.length === 0 && (
        <p className="text-gray-600">No pending requests.</p>
      )}

      {!loading && !error && requests.length > 0 && (
        <table className="min-w-full border text-sm bg-white rounded-md overflow-hidden">
          <thead className="bg-gray-100">
            <tr>
              <th className="border px-3 py-2 text-left">Title</th>
              <th className="border px-3 py-2 text-left">Author</th>
              <th className="border px-3 py-2 text-left">ISBN</th>
              <th className="border px-3 py-2 text-left">Notes</th>
              <th className="border px-3 py-2 text-left">Actions</th>
            </tr>
          </thead>

          <tbody>
            {requests.map((r) => (
              <tr key={r.request_id}>
                {/* Title (supports both backend formats) */}
                <td className="border px-3 py-2">
                  {r.book_title || r.title}
                </td>

                <td className="border px-3 py-2">{r.author}</td>

                <td className="border px-3 py-2">{r.isbn}</td>

                <td className="border px-3 py-2">
                  {r.notes || <span className="text-gray-400">—</span>}
                </td>

                <td className="border px-3 py-2 space-x-2">
                  <button
                    onClick={() => accept(r.request_id)}
                    className="bg-green-600 text-white px-3 py-1 rounded"
                  >
                    Accept
                  </button>

                  <button
                    onClick={() => remove(r.request_id)}
                    className="bg-red-600 text-white px-3 py-1 rounded"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
