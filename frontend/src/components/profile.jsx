"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

const UserIcon = () => (
  <svg
    width="70"
    height="70"
    viewBox="0 0 24 24"
    fill="none"
    stroke="#A46300"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="8" r="4" />
    <path d="M4 20c1.5-3 4-5 8-5s6.5 2 8 5" />
  </svg>
);

export default function ProfilePage() {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [lists, setLists] = useState([]);
  const [newListName, setNewListName] = useState("");
  const [creating, setCreating] = useState(false);


  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }

    async function loadUser() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(res.data);
      } catch (err) {
        router.push("/login");
      }
    }
    loadUser();
  }, [token, router]);


useEffect(() => {
  if (!user || !token) return;

  async function loadLists() {
    try {
      const res = await axios.get(
        "http://127.0.0.1:8000/readinglist/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setLists(res.data);
    } catch (err) {
      console.log(err);
    }
  }

  loadLists();
}, [user, token]);



  async function handleCreateList() {
    if (!newListName.trim()) return;

    try {
      await axios.post(
        "http://127.0.0.1:8000/readinglist/",
        { name: newListName },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setNewListName("");
      setCreating(false);

   
      const res = await axios.get("http://127.0.0.1:8000/readinglist/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setLists(res.data);
    } catch (err) {
      console.log(err);
      alert("Error adding reading list");
    }
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-[#FFF08A] p-12 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-10">Hi, {user.username}</h1>

      <div className="flex gap-12 items-stretch w-full max-w-6xl">
        {/* left box*/}
        <div className="flex-1 profile-card bg-white rounded-3xl p-10 flex flex-col items-center min-h-[650px] shadow-lg">
          <div className="mb-6">
            <UserIcon />
          </div>

          <label className="font-semibold w-full mb-1">Username</label>
          <input
            type="text"
            value={user.username}
            disabled
            className="w-full h-14 px-4 bg-gray-100 rounded-xl text-lg text-center mb-6 border border-gray-300"
          />

          <label className="font-semibold w-full mb-1">Email</label>
          <input
            type="text"
            value={user.email}
            disabled
            className="w-full h-14 px-4 bg-gray-100 rounded-xl text-lg text-center mb-6 border border-gray-300"
          />

          <button className="px-6 py-3 bg-gray-200 rounded-xl font-semibold mt-auto">
            Edit
          </button>
        </div>

        {/* right box*/}
        <div className="flex-1 readinglist-card bg-white rounded-3xl p-10 min-h-[650px] shadow-lg flex flex-col">
          <h2 className="text-3xl font-bold mb-4">Reading Lists</h2>

          {lists.length >= 10 && (
            <p className="text-red-600 mb-4">
              You can only have 10 reading lists
            </p>
          )}

          <div className="flex flex-col gap-2 mb-8">
            {lists.length === 0 && <p>No reading lists yet.</p>}

            {lists.map((list, i) => (
              <p key={i} className="text-lg">
                {i + 1}. {list.name} • {list.total_books} books{" "}
                {list.is_public ? "(public)" : "(private)"}
              </p>
            ))}
          </div>

          {/*list input*/}
          {!creating ? (
            <button
              onClick={() => setCreating(true)}
              disabled={lists.length >= 10}
              className="self-start bg-[#FFD52E] px-6 py-3 rounded-xl font-semibold hover:bg-yellow-400"
            >
              + Add Reading List
            </button>
          ) : (
            <div className="flex flex-col gap-3">
              <input
                type="text"
                value={newListName}
                onChange={(e) => setNewListName(e.target.value)}
                className="w-full h-12 px-4 border rounded-xl"
                placeholder="New list name"
              />
              <div className="flex gap-3">
                <button
                  onClick={handleCreateList}
                  className="bg-[#FFD52E] px-5 py-2 rounded-xl font-semibold hover:bg-yellow-400"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setCreating(false);
                    setNewListName("");
                  }}
                  className="text-gray-700 px-4 py-3"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
