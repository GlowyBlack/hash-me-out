"use client";

import { useState, useEffect, useRef } from "react";

export default function Users() {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const searchRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setResults([]);
        setIsTyping(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Live search (debounced)
  useEffect(() => {
    if (!search.trim()) {
      setResults([]);
      return;
    }

    setIsTyping(true);
    const token = localStorage.getItem("access_token");

    const timeout = setTimeout(async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/auth/search?username=${encodeURIComponent(search)}`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        const data = await res.json();
        setResults(data);
      } catch (err) {
        console.error("Failed to search users:", err);
        setResults([]);
      }
      setIsTyping(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, [search]);

  // Suspend user
  async function suspendUser(userId) {
    const duration = prompt("Enter suspension duration in minutes:", "60");
    if (!duration) return;

    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(
        `http://localhost:8000/auth/suspend/${userId}?duration_minutes=${duration}`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        alert("Failed to suspend user: " + (errorData.detail || res.statusText));
        return;
      }

      const data = await res.json();

      // Update selectedUser directly with the API response
      setSelectedUser(prev => ({
        ...prev,
        is_suspended: true,
        suspended_until: data.suspended_until,
      }));

      // Update results list too
      setResults(prev =>
        prev.map(u =>
          u.id === userId
            ? { ...u, is_suspended: true, suspended_until: data.suspended_until }
            : u
        )
      );

    } catch (err) {
      console.error(err);
    }
  }

  // Unsuspend user
  async function unsuspendUser(userId) {
    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(
        `http://localhost:8000/auth/unsuspend/${userId}`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!res.ok) {
        const errorData = await res.json();
        alert("Failed to unsuspend user: " + (errorData.detail || res.statusText));
        return;
      }

      // Update selected user
      setSelectedUser(prev => ({
        ...prev,
        is_suspended: false,
        suspended_until: null,
      }));

      // Update results list
      setResults(prev =>
        prev.map(u =>
          u.id === userId
            ? { ...u, is_suspended: false, suspended_until: null }
            : u
        )
      );

    } catch (err) {
      console.error(err);
    }
  }

  return (
    <div className="max-w-2xl mx-auto mt-6" ref={searchRef}>
      <h1 className="text-3xl font-bold mb-6">User Management</h1>

      <input
        type="text"
        placeholder="Search by username..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full px-4 py-2 mb-4 border border-gray-300 rounded-lg bg-gray-50"
      />

      {isTyping && <p className="text-sm text-gray-500 mb-2">Searching...</p>}

      <div className="bg-white p-4 rounded-lg shadow-md">
        {results.length === 0 ? (
          <p className="text-gray-600">No users found.</p>
        ) : (
          <ul className="divide-y">
            {results.map((user) => (
              <li
                key={user.id}
                className="py-3 cursor-pointer hover:bg-gray-100"
                onClick={() => setSelectedUser(user)}
              >
                <p className="font-medium">{user.username}</p>
                <p className="text-sm text-gray-500">{user.email}</p>
              </li>
            ))}
          </ul>
        )}
      </div>

      {selectedUser && (
        <div className="relative mt-6 bg-gray-50 p-20 rounded-lg shadow-md">
          {/* Close */}
          <button
            onClick={() => setSelectedUser(null)}
            className="absolute top-2 right-5 text-gray-500 hover:text-gray-800 font-bold text-3xl"
          >
            ×
          </button>

          <h2 className="text-4xl font-bold mb-4">User Details</h2>
          <p className="text-xl"><strong>ID:</strong> {selectedUser.id}</p>
          <p className="text-xl"><strong>Username:</strong> {selectedUser.username}</p>
          <p className="text-xl"><strong>Email:</strong> {selectedUser.email}</p>
          <p className="text-xl"><strong>Admin:</strong> {selectedUser.is_admin ? "Yes" : "No"}</p>
          <p className="text-xl"><strong>Suspended:</strong> {selectedUser.is_suspended ? "Yes" : "No"}</p>
          <p className="text-xl"><strong>Suspended Until:</strong> {selectedUser.suspended_until ? new Date(selectedUser.suspended_until).toLocaleString() : "N/A"}</p>
          <p className="text-xl"><strong>Warnings:</strong> {selectedUser.warnings || "N/A"}</p>

          {/* Action buttons */}
          {!selectedUser.is_suspended ? (
            <button
              onClick={() => suspendUser(selectedUser.id)}
              className="mt-6 px-4 py-3 bg-red-600 text-white font-semibold rounded hover:bg-red-300 transition"
            >
              Suspend User
            </button>
          ) : (
            <button
              onClick={() => unsuspendUser(selectedUser.id)}
              className="mt-6 px-4 py-3 bg-green-600 text-white font-semibold rounded hover:bg-green-300 transition"
            >
              Unsuspend User
            </button>
          )}
        </div>
      )}
    </div>
  );
}
