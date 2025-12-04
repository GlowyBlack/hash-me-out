"use client";

import { useEffect, useState } from "react";

export default function Suspensions() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  async function fetchSuspended() {
    try {
      const res = await fetch("http://localhost:8000/auth/suspended", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      const data = await res.json();
      if (Array.isArray(data)) {
        setUsers(data);
      } else {
        console.error("Not an array:", data);
        setUsers([]);
      }
    } catch (err) {
      console.error("Error fetching:", err);
    } finally {
      setLoading(false);
    }
  }

  async function unsuspendUser(id) {
    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(
        `http://localhost:8000/auth/unsuspend/${id}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        alert(
          "Could not unsuspend user: " +
            (errorData.detail || res.statusText)
        );
        return;
      }

      setUsers((prev) => prev.filter((u) => u.id !== id));
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    fetchSuspended();
  }, []);

  if (loading) return <p className="p-4">Loading...</p>;

  return (
    <div className="p-6">
      <h1 className="text-gray-800 text-3xl font-bold mb-6">Suspended Users</h1>

      {users.length === 0 ? (
        <p className="text-gray-800">No suspended users.</p>
      ) : (
        <div className="space-y-6">
          {users.map((u) => (
            <div
              key={u.id}
              className="border rounded-lg p-4 shadow-sm bg-gray-50 min-h-[120px]"
            >
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-xl font-semibold">{u.username}</p>
                  <p className="text-gray-800">{u.email}</p>

                  <p className="mt-2 text-sm">
                    <strong>Suspended:</strong>{" "}
                    {u.is_suspended ? "Yes" : "No"}
                  </p>

                  <p className="mt-2 text-sm">
                    <strong>Suspended Until:</strong>{" "}
                    {u.suspended_until
                      ? new Date(u.suspended_until).toLocaleString()
                      : "N/A"}
                  </p>

                  <p className="mt-1 text-sm">
                    <strong>Suspension Reason:</strong>{" "}
                    {u.suspension_reason || "N/A"}
                  </p>

                  <p className="mt-1 text-sm">
                    <strong>Warnings:</strong> {u.warnings}
                  </p>
                </div>

                <button
                  onClick={() => unsuspendUser(u.id)}
                  className="rounded-full border border-slate-400 bg-white text-slate-800 text-base font-semibold px-8 py-4 hover:bg-slate-50 transition"
                >
                  Unsuspend
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
