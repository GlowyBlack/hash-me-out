
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function AddToReadingListButton({ book, user, onRequireAuth }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [lists, setLists] = useState([]);
  const [loadingLists, setLoadingLists] = useState(false);
  const [selectedListId, setSelectedListId] = useState(null);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const API_BASE =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  async function handleClick() {
    if (!user) {
      if (onRequireAuth) onRequireAuth();
      return;
    }

    setOpen(true);
    setMessage(null);
    setErrorMsg(null);

    await fetchLists();
  }

  async function fetchLists() {
    try {
      setLoadingLists(true);
      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;

      if (!token) {
        if (onRequireAuth) onRequireAuth();
        return;
      }

      const res = await fetch(`${API_BASE}/readinglist`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        cache: "no-store",
      });

      if (!res.ok) {
        console.error("Failed to load reading lists", res.status);
        setErrorMsg("Could not load your reading lists.");
        setLists([]);
        return;
      }

      const data = await res.json(); 
      setLists(Array.isArray(data) ? data : []);
      if (Array.isArray(data) && data.length > 0) {
        setSelectedListId(data[0].list_id);
      }
    } catch (e) {
      console.error("Error fetching reading lists", e);
      setErrorMsg("Unexpected error loading lists.");
    } finally {
      setLoadingLists(false);
    }
  }

  async function handleAdd() {
    if (!selectedListId) return;

    try {
      setAdding(true);
      setMessage(null);
      setErrorMsg(null);

      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("access_token")
          : null;

      if (!token) {
        if (onRequireAuth) onRequireAuth();
        return;
      }

      const res = await fetch(
        `${API_BASE}/readinglist/${selectedListId}/books/${encodeURIComponent(
          book.isbn
        )}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        console.error(
          "Failed to add book to reading list",
          res.status,
          res.statusText,
          err
        );
        const msg =
          typeof err.detail === "string"
            ? err.detail
            : "Could not add book to reading list.";
        setErrorMsg(msg);
        return;
      }

      setMessage("Book added to your list!");
    } catch (e) {
      console.error("Error adding to reading list", e);
      setErrorMsg("Unexpected error while adding.");
    } finally {
      setAdding(false);
    }
  }

  function handleGoToReadingLists() {
    router.push("/readinglists");
  }

  return (
    <>
      <button
        type="button"
        onClick={handleClick}
        className="inline-flex items-center justify-center rounded-full bg-white/90 hover:bg-white shadow-md border border-slate-200 w-10 h-10 text-slate-700 text-2xl leading-none"
        title="Add to reading list"
      >
        +
      </button>

      {open && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30">
          <div className="w-full max-w-sm rounded-2xl bg-white shadow-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-slate-900">
                Add to reading list
              </h2>
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  setMessage(null);
                  setErrorMsg(null);
                }}
                className="text-slate-400 hover:text-slate-600 text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-600 mb-3">
              {book.book_title} ({book.isbn})
            </p>

            {loadingLists && (
              <p className="text-xs text-slate-500 mb-3">Loading lists…</p>
            )}

            {!loadingLists && lists.length === 0 && (
              <div className="mb-3 text-xs text-slate-600 space-y-2">
                <p>You don&apos;t have any reading lists yet.</p>
                <button
                  type="button"
                  onClick={handleGoToReadingLists}
                  className="inline-flex items-center rounded-full border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  Go to Reading Lists
                </button>
              </div>
            )}

            {!loadingLists && lists.length > 0 && (
              <div className="mb-3">
                <label
                  htmlFor="readinglist-select"
                  className="block text-xs font-medium text-slate-700 mb-1"
                >
                  Choose a list
                </label>
                <select
                  id="readinglist-select"
                  className="w-full rounded-lg border border-slate-300 px-2 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-300 focus:border-amber-400"
                  value={selectedListId ?? ""}
                  onChange={(e) =>
                    setSelectedListId(
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                >
                  {lists.map((l) => (
                    <option key={l.list_id} value={l.list_id}>
                      {l.name} ({l.total_books} books)
                    </option>
                  ))}
                </select>
              </div>
            )}

            {errorMsg && (
              <p className="text-xs text-red-500 mb-2">{errorMsg}</p>
            )}
            {message && (
              <p className="text-xs text-emerald-600 mb-2">{message}</p>
            )}

            <div className="mt-2 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  setMessage(null);
                  setErrorMsg(null);
                }}
                className="text-xs px-3 py-1 rounded-full border border-slate-300 text-slate-700 hover:bg-slate-50"
              >
                Close
              </button>
              <button
                type="button"
                onClick={handleAdd}
                disabled={adding || !selectedListId || lists.length === 0}
                className="text-xs px-3 py-1 rounded-full bg-[#ffb803] border border-[#ffb803] text-slate-900 font-semibold hover:bg-[#f5a800] hover:border-[#f5a800] disabled:opacity-60 disabled:cursor-default"
              >
                {adding ? "Adding…" : "Add"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
