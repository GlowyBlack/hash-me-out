"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import Header from "../../components/Header";

export default function UserSearch() {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [tokenChecked, setTokenChecked] = useState(false);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    const stored = localStorage.getItem("access_token");
    setToken(stored);
    setTokenChecked(true);
  }, []);

  useEffect(() => {
    if (!tokenChecked || !token) return;

    async function fetchUser() {
      try {
        const res = await axios.get(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(res.data);
      } catch (err) {
        localStorage.removeItem("access_token");
        setUser(null);
      }
    }

    fetchUser();
  }, [tokenChecked, token]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setToken(null);
    setResults([]);
  };

  const goToProfile = () => {
    router.push("/profile");
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (!token) {
      setError("You must be logged in to search.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await axios.get(
        `${API_BASE}/auth/search-users?username=${encodeURIComponent(query)}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      const users = Array.isArray(res.data) ? res.data : [res.data];

      const enhanced = await Promise.all(
        users.map(async (u) => {
          const userId = u.id;

          if (!userId) {
            return { ...u, publicLists: [] };
          }

          try {
            const listsRes = await axios.get(
              `${API_BASE}/readinglist/public/${userId}`
            );
            const publicLists = Array.isArray(listsRes.data)
              ? listsRes.data
              : [];

            return { ...u, publicLists };
          } catch {
            return { ...u, publicLists: [] };
          }
        })
      );

      setResults(enhanced);
    } catch (err) {
      setError(err.response?.data?.detail || "Error fetching users");
      setResults([]);
    }

    setLoading(false);
  };

  if (!tokenChecked) return null;

  return (
    <div className="min-h-screen bg-[#F7F9FC]">
      <Header user={user} handleLogout={handleLogout} goToProfile={goToProfile} />

      <div className="pt-40 px-6 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Connect with Other Users</h1>
        <p className="mb-4 text-gray-700">
          Search for registered users and see their public reading lists.
        </p>

        <form onSubmit={handleSearch} className="flex gap-2 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by username"
            className="flex-1 border rounded px-3 py-2"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-yellow-400 text-gray-900 font-bold rounded-xl hover:bg-yellow-500 transition"
          >
            Search
          </button>
        </form>

        {loading && <p>Loading...</p>}
        {error && <p className="text-red-600">{error}</p>}

        <div className="space-y-4">
          {results.map((u) => {
            const hasPublicLists =
              Array.isArray(u.publicLists) && u.publicLists.length > 0;

            return (
              <div
                key={u.id}
                className="p-4 bg-white shadow-sm rounded-md border"
              >
                <h2 className="text-lg font-semibold">{u.username}</h2>

                {hasPublicLists ? (
                  <div className="mt-2 space-y-2">
                    {u.publicLists.map((list) => (
                      <button
                        key={list.list_id}
                        onClick={() =>
                          router.push(
                            `/readinglist/public/${list.list_id}?owner=${u.id}`
                          )
                        }
                        className="w-full text-left p-3 rounded-md border hover:bg-slate-50 transition"
                      >
                        <h3 className="font-semibold">{list.name}</h3>
                        <p className="text-gray-700">
                          {list.total_books}{" "}
                          {list.total_books === 1 ? "book" : "books"}
                        </p>
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 mt-1">No public reading list</p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
