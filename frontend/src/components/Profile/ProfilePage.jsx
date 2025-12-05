"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";

const UserIcon = () => (
  <div className="w-24 h-24 rounded-full bg-[#E3F0FF] flex items-center justify-center mb-4">
    <svg
      width="54"
      height="54"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#4B7BE5"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20c1.5-3 4-5 8-5s6.5 2 8 5" />
    </svg>
  </div>
);

const Kebab = () => (
  <svg
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="#526187"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="5" r="1" />
    <circle cx="12" cy="12" r="1" />
    <circle cx="12" cy="19" r="1" />
  </svg>
);

export default function ProfilePage() {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [lists, setLists] = useState([]);
  const [creating, setCreating] = useState(false);
  const [newListName, setNewListName] = useState("");
  const [openMenuId, setOpenMenuId] = useState(null);

  const [isEditing, setIsEditing] = useState(false);
  const [editedUsername, setEditedUsername] = useState("");
  const [editedEmail, setEditedEmail] = useState("");

  const [formType, setFormType] = useState("login");

  const [page, setPage] = useState(0);
  const PAGE_SIZE = 5;

  // NEW: keep token in state and load it once on mount
  const [token, setToken] = useState(null);
  const [tokenChecked, setTokenChecked] = useState(false);

  const API_BASE = "http://localhost:8000";

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/");
  };

  // Load token from localStorage on mount
  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = localStorage.getItem("access_token");
    console.log("[Profile] Loaded token from localStorage:", stored ? "(present)" : "(none)");
    setToken(stored);
    setTokenChecked(true);
  }, []);

  // Build auth headers whenever token changes
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  // Load current user
  useEffect(() => {
    // Wait until we’ve checked localStorage
    if (!tokenChecked) return;

    // If no token at all, bounce to landing
    if (!token) {
      console.log("[Profile] No token found → redirecting to /");
      router.push("/");
      return;
    }

    async function loadUser() {
      try {
        console.log("[Profile] Calling /auth/me with Authorization: Bearer <token>");
        const res = await axios.get(`${API_BASE}/auth/me`, {
          headers: authHeaders,
        });
        console.log("[Profile] /auth/me status:", res.status, "data:", res.data);
        setUser(res.data);
        setEditedUsername(res.data.username);
        setEditedEmail(res.data.email);
      } catch (err) {
        console.error("[Profile] /auth/me failed:", err.response?.status, err.response?.data);
        localStorage.removeItem("access_token");
        setUser(null);
        router.push("/");
      }
    }

    loadUser();
  }, [tokenChecked, token, router]); // re-run if token changes

  // Load reading lists once user + token are ready
  useEffect(() => {
    if (!user || !token) return;

    async function loadLists() {
      try {
        console.log("[Profile] Loading reading lists");
        const res = await axios.get(`${API_BASE}/readinglist/`, {
          headers: authHeaders,
        });
        setLists(res.data);
      } catch (err) {
        console.log("[Profile] Failed to load reading lists:", err.response?.status, err.response?.data);
      }
    }

    loadLists();
  }, [user, token]);

  useEffect(() => {
    const maxPage = Math.max(0, Math.ceil(lists.length / PAGE_SIZE) - 1);
    setPage((p) => (p > maxPage ? maxPage : p));
  }, [lists.length]);

  async function reloadLists() {
    if (!token) return;
    try {
      const res = await axios.get(`${API_BASE}/readinglist/`, {
        headers: authHeaders,
      });
      setLists(res.data);
    } catch (err) {
      console.log("[Profile] reloadLists error:", err.response?.status, err.response?.data);
    }
  }

  async function handleDownloadList(listId, listName) {
    if (!token) return;

    try {
      const res = await axios.get(`${API_BASE}/readinglist/${listId}/download`, {
        headers: authHeaders,
        responseType: "blob", // important for downloading files
      });

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      const safeName = listName.replace(/\s+/g, "_").replace(/\//g, "_");
      link.href = url;
      link.setAttribute("download", `${safeName}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("[Profile] handleDownloadList error:", err.response?.status, err.response?.data);
      alert(err.response?.data?.detail || "Error downloading reading list");
    }
  }
  
async function handleSaveProfile() {
    try {
      const payload = {};
      if (editedUsername.trim() && editedUsername !== user.username) {
        payload.username = editedUsername.trim();
      }
      if (editedEmail.trim() && editedEmail !== user.email) {
        payload.email = editedEmail.trim();
      }

      if (Object.keys(payload).length === 0) {
        setIsEditing(false);
        return;
      }

      const res = await axios.put(`${API_BASE}/auth/me`, payload, {
        headers: {
          ...authHeaders,
          "Content-Type": "application/json",
        },
      });

      setUser(res.data);
      setIsEditing(false);
    } catch (err) {
      console.log("[Profile] handleSaveProfile error:", err.response?.status, err.response?.data);
      alert(err.response?.data?.detail || "Error updating profile");
    }
  }

  async function handleCreateList() {
    if (!newListName.trim()) {
      return;
    }

    try {
      await axios.post(
        `${API_BASE}/readinglist/`,
        { name: newListName.trim() },
        { headers: authHeaders },
      );

      setNewListName("");
      setCreating(false);
      await reloadLists();
    } catch (err) {
      console.log("[Profile] handleCreateList error:", err.response?.status, err.response?.data);
      alert(err.response?.data?.detail || "Error adding reading list");
    }
  }

  async function handleDeleteList(listId) {
    const confirmed = window.confirm("Delete this reading list?");
    if (!confirmed) {
      return;
    }

    try {
      await axios.delete(`${API_BASE}/readinglist/${listId}`, {
        headers: authHeaders,
      });
      setOpenMenuId(null);
      await reloadLists();
    } catch (err) {
      console.log("[Profile] handleDeleteList error:", err.response?.status, err.response?.data);
      alert(err.response?.data?.detail || "Error deleting reading list");
    }
  }

  async function handleToggleVisibility(listId) {
    try {
      const res = await axios.put(
        `${API_BASE}/readinglist/${listId}/visibility`,
        {},
        { headers: authHeaders },
      );

      setOpenMenuId(null);

      if (res.data && typeof res.data === "object") {
        setLists((prev) =>
          prev.map((l) =>
            (l.id ?? l.list_id) === listId ? { ...l, ...res.data } : l,
          ),
        );
      } else {
        await reloadLists();
      }
    } catch (err) {
      console.log("[Profile] handleToggleVisibility error:", err.response?.status, err.response?.data);
      alert(err.response?.data?.detail || "Error updating visibility");
    }
  }

  // While we haven’t checked token yet, render nothing (avoid flicker)
  if (!tokenChecked) {
    return null;
  }

  // If tokenChecked is true but user still not loaded (because /auth/me failed),
  // the effect above will already have redirected; we can just render nothing here.
  if (!user) {
    return null;
  }

  const displayName =
    user.username?.charAt(0).toUpperCase() + user.username?.slice(1);

  const totalPages = Math.max(1, Math.ceil(lists.length / PAGE_SIZE));
  const startIndex = page * PAGE_SIZE;
  const visibleLists = lists.slice(startIndex, startIndex + PAGE_SIZE);
  const canPrev = page > 0;
  const canNext = page < totalPages - 1;

  return (
    <div className="min-h-screen bg-[#F7F9FC]">
      <Header
        user={user}
        setFormType={setFormType}
        handleLogout={handleLogout}
        compact={true}
        showProfileButton={false}
      />

      <main className="max-w-6xl mx-auto px-6 pb-16">
        <h1 className="text-3xl font-extrabold mb-8 py-6">Hi, {displayName}</h1>

        <div className="flex flex-col lg:flex-row gap-10 items-start">
          {/* profile card */}
          <div className="flex-1 max-w-sm">
            <section className="bg-white rounded-3xl p-8 shadow-[0_18px_40px_rgba(15,35,52,0.08)] border border-[#E4ECFF] flex flex-col items-center">
              <UserIcon />

              {isEditing ? (
                <>
                  <input
                    type="text"
                    value={editedUsername}
                    onChange={(e) => setEditedUsername(e.target.value)}
                    className="w-full mt-1 mb-2 px-3 py-2 rounded-xl border border-[#D4DDED] text-center text-base"
                  />
                  <input
                    type="email"
                    value={editedEmail}
                    onChange={(e) => setEditedEmail(e.target.value)}
                    className="w-full mb-4 px-3 py-2 rounded-xl border border-[#D4DDED] text-center text-sm"
                  />
                </>
              ) : (
                <>
                  <div className="text-xl font-bold text-[#14213D]">
                    {user.username}
                  </div>
                  <div className="text-sm text-[#526187] mb-6">
                    {user.email}
                  </div>
                </>
              )}

              <div className="flex gap-3 mt-2 w-full justify-center">
                {!isEditing ? (
                  <button
                    className="px-5 py-2 rounded-xl border border-[#D4DDED] bg-white text-sm font-semibold text-[#14213D]"
                    onClick={() => setIsEditing(true)}
                  >
                    Edit
                  </button>
                ) : (
                  <>
                    <button
                      className="px-5 py-2 rounded-xl border border-[#D4DDED] bg-white text-sm font-semibold text-[#14213D]"
                      onClick={() => {
                        setIsEditing(false);
                        setEditedUsername(user.username);
                        setEditedEmail(user.email);
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      className="px-5 py-2 rounded-xl bg-[#FFD52E] text-sm font-semibold text-[#14213D] hover:bg-[#FFC81C]"
                      onClick={handleSaveProfile}
                    >
                      Save
                    </button>
                  </>
                )}
              </div>
            </section>
          </div>

          {/* reading lists */}
          <section className="flex-1 w-full">
            <div className="flex items-center justify-between mb-4 gap-4">
              <h2 className="text-2xl font-bold text-[#14213D]">
                Reading Lists
              </h2>

              {!creating && (
                <button
                  onClick={() => setCreating(true)}
                  disabled={lists.length >= 10}
                  className="h-10 px-4 rounded-xl bg-[#FFD52E] text-sm font-semibold text-[#14213D] hover:bg-[#FFC81C] disabled:opacity-60 whitespace-nowrap"
                >
                  Add New List
                </button>
              )}
            </div>

            {creating && (
              <div className="flex flex-col sm:flex-row gap-3 mb-5">
                <input
                  type="text"
                  value={newListName}
                  onChange={(e) => setNewListName(e.target.value)}
                  className="flex-1 h-11 px-4 border border-[#D4DDED] rounded-xl text-sm"
                  placeholder="New list name"
                />
                <div className="flex gap-3">
                  <button
                    onClick={handleCreateList}
                    className="h-11 px-4 rounded-xl bg-[#FFD52E] text-sm font-semibold text-[#14213D] hover:bg-[#FFC81C]"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setCreating(false);
                      setNewListName("");
                    }}
                    className="h-11 px-4 rounded-xl border border-[#D4DDED] bg-white text-sm font-semibold text-[#14213D]"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {lists.length === 0 && !creating && (
              <p className="text-sm text-[#526187] mb-4">
                No reading lists yet.
              </p>
            )}

            <div className="flex flex-col gap-3 mb-6">
              {visibleLists.map((list, i) => {
                const id = list.id ?? list.list_id ?? i;

                return (
                  <div
                    key={id}
                    onClick={() => router.push(`/readinglist/${id}`)}
                    className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-[#E4ECFF] bg-[#F9FBFF] relative cursor-pointer hover:bg-[#F5F7FF]"
                  >
                    <div className="flex flex-col">
                      <span className="text-sm font-medium text-[#14213D]">
                        {list.name}
                      </span>
                      <span className="text-xs text-[#74819A]">
                        {list.total_books} book
                        {list.total_books === 1 ? "" : "s"} ·{" "}
                        {list.is_public ? "Public" : "Private"}
                      </span>
                    </div>

                    <button
                      type="button"
                      className="p-1 rounded-full hover:bg-[#E4ECFF]"
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenMenuId((prev) => (prev === id ? null : id));
                      }}
                    >
                      <Kebab />
                    </button>

                    {openMenuId === id && (
                    <div className="absolute right-3 top-11 z-10 w-44 bg-white border border-[#E4ECFF] rounded-xl shadow-md text-sm">
                      <button
                        className="w-full text-left px-3 py-2 hover:bg-[#F3F6FF]"
                        onClick={() => handleToggleVisibility(id)}
                      >
                        Toggle visibility
                      </button>
                      <button
                        className="w-full text-left px-3 py-2 hover:bg-[#E4ECFF]"
                        onClick={() => handleDownloadList(id, list.name)}
                      >
                        Download list
                      </button>
                      <button
                        className="w-full text-left px-3 py-2 hover:bg-[#FFE6E6] text-red-600"
                        onClick={() => handleDeleteList(id)}
                      >
                        Delete list
                      </button>
                    </div>
                  )}

                  </div>
                );
              })}
            </div>

            {lists.length > PAGE_SIZE && (
              <div className="flex items-center justify-end gap-4">
                <button
                  type="button"
                  onClick={() => canPrev && setPage((p) => p - 1)}
                  disabled={!canPrev}
                  className="text-sm font-semibold text-[#1751FF] disabled:text-gray-300"
                >
                  Previous
                </button>

                <span className="text-xs text-[#74819A]">
                  Page {page + 1} of {totalPages}
                </span>

                <button
                  type="button"
                  onClick={() => canNext && setPage((p) => p + 1)}
                  disabled={!canNext}
                  className="flex items-center gap-1 text-sm font-semibold text-[#1751FF] disabled:text-gray-300"
                >
                  Next <span>→</span>
                </button>
              </div>
            )}

            {lists.length >= 10 && (
              <p className="text-xs text-red-600 mt-3">
                You can only have 10 reading lists.
              </p>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
