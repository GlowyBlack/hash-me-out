"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import Header from "@/components/Header";

const BookIcon = () => (
  <div className="w-12 h-12 rounded-2xl bg-[#FFF6D6] flex items-center justify-center">
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#F4B000"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M6 4h11a1 1 0 0 1 1 1v13" />
      <path d="M6 4v13a1 1 0 0 0 1 1h11" />
      <line x1="9" y1="8" x2="15" y2="8" />
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
    <circle cx="12" cy="5" r="1.5" />
    <circle cx="12" cy="12" r="1.5" />
    <circle cx="12" cy="19" r="1.5" />
  </svg>
);

export default function ReadingListView({ listId }) {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [list, setList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [formType, setFormType] = useState("login");
  const [openMenuIsbn, setOpenMenuIsbn] = useState(null); // which book's menu is open

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.push("/homepage");
  };

  useEffect(() => {
    if (!token) {
      router.push("/homepage");
      return;
    }

    async function loadUser() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/auth/me", {
          headers: authHeaders,
        });
        setUser(res.data);
      } catch {
        router.push("/homepage");
      }
    }

    loadUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!user || !token || !listId) return;

    async function loadList() {
      try {
        const res = await axios.get(
          `http://127.0.0.1:8000/readinglist/${listId}`,
          {
            params: { user_id: user.id },
            headers: authHeaders,
          }
        );
        setList(res.data);
      } catch {
        alert("Unable to load reading list.");
        router.push("/profile");
      } finally {
        setLoading(false);
      }
    }

    loadList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  async function handleToggleVisibility() {
    if (!list) return;
    setToggling(true);

    try {
      const res = await axios.put(
        `http://127.0.0.1:8000/readinglist/${listId}/visibility`,
        {},
        { headers: authHeaders }
      );

      setList((prev) =>
        prev
          ? {
              ...prev,
              is_public:
                typeof res.data.is_public === "boolean"
                  ? res.data.is_public
                  : !prev.is_public,
            }
          : prev
      );
    } catch (err) {
      alert(err.response?.data?.detail || "Error updating visibility");
    } finally {
      setToggling(false);
    }
  }

  function handleOpenBook(book) {
    if (!book?.isbn) return;
    router.push(`/books/${book.isbn}`);
  }

  async function handleRemoveBook(e, book) {
    e.stopPropagation(); // don't trigger the row click
    if (!book?.isbn) return;

    try {
      await axios.delete(
        `http://127.0.0.1:8000/readinglist/${listId}/books/${book.isbn}`,
        { headers: authHeaders }
      );

      setList((prev) =>
        prev
          ? {
              ...prev,
              books: (prev.books || []).filter(
                (b) => b.isbn !== book.isbn
              ),
            }
          : prev
      );
      setOpenMenuIsbn(null);
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          "Error removing book from reading list"
      );
    }
  }

  if (!user || loading) {
    return (
      <div className="min-h-screen bg-[#F7F9FC]">
        <Header
          user={user}
          setFormType={setFormType}
          handleLogout={handleLogout}
          compact
          showProfileButton={false}
        />
      </div>
    );
  }

  if (!list) {
    return (
      <div className="min-h-screen bg-[#F7F9FC]">
        <Header
          user={user}
          setFormType={setFormType}
          handleLogout={handleLogout}
          compact
          showProfileButton={false}
        />
        <main className="max-w-3xl mx-auto px-6 pt-12">
          <p className="text-sm text-[#526187]">Reading list not found.</p>
        </main>
      </div>
    );
  }

  const books = list.books || [];

  return (
    <div className="min-h-screen bg-[#F7F9FC]">
      <Header
        user={user}
        setFormType={setFormType}
        handleLogout={handleLogout}
        compact
        showProfileButton={false}
      />

      <main className="max-w-3xl mx-auto px-6 pt-28 pb-16">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-[#9AA4BD]">
              Reading list
            </p>
            <h1 className="text-3xl font-extrabold text-[#14213D] mt-1">
              {list.name}
            </h1>
          </div>

          <button
            onClick={handleToggleVisibility}
            disabled={toggling}
            className={`px-5 py-2 rounded-full text-sm font-semibold shadow-sm border transition ${
              list.is_public
                ? "bg-white border-[#FFD52E] text-[#856000]"
                : "bg-[#FFD52E] border-[#FFD52E] text-[#14213D]"
            } ${toggling ? "opacity-70 cursor-wait" : ""}`}
          >
            {list.is_public ? "Public" : "Private"}
          </button>
        </div>

        {/* Books */}
        <section className="bg-white rounded-3xl border border-[#E4ECFF] shadow-[0_18px_40px_rgba(15,35,52,0.08)] overflow-hidden">
          {books.length === 0 ? (
            <div className="px-8 py-10 text-center">
              <p className="text-sm text-[#74819A]">
                No books in this list yet.
              </p>
            </div>
          ) : (
            books.map((book, index) => {
              const isLast = index === books.length - 1;

              const rating =
                book.user_rating ??
                book.rating ??
                book.score ??
                book.my_rating ??
                null;

              const isbnKey = book.isbn ?? `${index}`;

              return (
                <div
                  key={isbnKey}
                  onClick={() => handleOpenBook(book)}
                  className={`w-full px-6 py-5 flex items-center justify-between gap-4 hover:bg-[#FFF9E6] transition cursor-pointer ${
                    !isLast ? "border-b border-[#F1F3FF]" : ""
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <BookIcon />
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold text-[#14213D]">
                        {book.book_title ?? book.title ?? "Untitled"}
                      </span>
                      <span className="text-xs text-[#74819A] mt-0.5">
                        {book.author ?? book.author_name ?? "Unknown author"}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {/* rating moved slightly left, before kebab */}
                    <span className="inline-flex items-center justify-center px-3 py-1 rounded-full bg-[#FFD52E] text-[#14213D] text-xs font-semibold">
                      {rating != null ? `${rating}/10` : "No rating"}
                    </span>

                    <div className="relative">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setOpenMenuIsbn((prev) =>
                            prev === isbnKey ? null : isbnKey
                          );
                        }}
                        className="p-1 rounded-full hover:bg-[#FFF2B8] transition"
                      >
                        <Kebab />
                      </button>

                      {openMenuIsbn === isbnKey && (
                        <div className="absolute right-0 mt-1 w-40 bg-white rounded-xl shadow-lg border border-[#E4ECFF] z-10">
                          <button
                            type="button"
                            onClick={(e) => handleRemoveBook(e, book)}
                            className="w-full text-left px-4 py-2 text-xs text-[#D12C2C] hover:bg-[#FFF5F5] rounded-xl"
                          >
                            Remove
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </section>
      </main>
    </div>
  );
}
