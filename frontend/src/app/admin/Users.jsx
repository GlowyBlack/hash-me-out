"use client";

import { useState } from "react";

export default function Users() {
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();

    // TODO: Replace with your API route (example)
    const res = await fetch(`/api/admin/users?username=${search}`);
    const data = await res.json();
    setResults(data);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">User Management</h1>

      <form onSubmit={handleSearch} className="flex mb-6">
        <input
          type="text"
          placeholder="Search by username..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-80 px-4 py-2 border border-gray-300 rounded-l-lg bg-gray-50"
        />
        <button
          type="submit"
          className="px-6 bg-yellow-400 hover:bg-yellow-500 rounded-r-lg font-semibold"
        >
          Search
        </button>
      </form>

      {/* Display results */}
      <div className="bg-white p-4 rounded-lg shadow-md">
        {results.length === 0 ? (
          <p className="text-gray-600">No users found.</p>
        ) : (
          <ul className="divide-y">
            {results.map((user) => (
              <li key={user.id} className="py-3">
                <p className="font-medium">{user.username}</p>
                <p className="text-sm text-gray-500">{user.email}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
