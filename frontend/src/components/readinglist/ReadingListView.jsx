"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import Header from "@/components/Header";

const BookIcon = () => (
  <div className="w-16 h-16 rounded-2xl bg-[#E3F0FF] flex items-center justify-center">
    <svg
      width="32"
      height="32"
      viewBox="0 0 24 24"
      fill="none"
      stroke="#4B7BE5"
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

export default function ReadingListView({ listId }) {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [list, setList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(false);
  const [formType, setFormType] = useState("login");

  // pagination for books
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 5;

  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.push("/homepage");
  };

  // 1. Load user
  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }

    async function loadUser() {
      try {
        const res = await axios.get("http://127.0.0.1:8000/auth/me", {
          headers: authHeaders,
        });
        setUser(res.data);
      } catch {
        router.push("/login");
      }
    }

    loadUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, router]);

  // 2. Load reading list detail
  useEffect(() => {
    if (!user || !token || !listId) return;

    async function loadList() {
      try {
        const res = await axios.get(
          `http://127.0.0.1:8000/readinglist/${listId}`,
          {
            params: { user_id: user.id },
            headers: authHeaders,
          },
        );
        setList(res.data);
        setLoading(false);
      } catch (err) {
        console.log(err);
        setLoading(false);
        alert("Unable to load reading list.");
        router.push("/profile");
      }
    }

    loadList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, token, listId]);

  // keep book page index in range
  useEffect(() => {
    if (!list || !list.books) return;
    const maxPage = Math.max(0, Math.ceil(list.books.length / PAGE_SIZE) - 1);
    setPage((p) => (p > maxPage ? maxPage : p));
  }, [list?.books?.length]);

  async function handleToggleVisibility() {
    if (!list) return;
      setToggling(true);
    try {
      const res = await axios.put(
        `http://127.0.0.1:8000/readinglist/${listId}/visibility`,
        {},
        { headers: authHeaders },
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
          : prev,
      );
    } catch (err) {
      console.log(err);
      alert(err.response?.data?.detail || "Error updating visibility");
    } finally {
      setToggling(false);
    }
  }

  function handleOpenBook(book) {
    if (!book?.isbn) return;
    router.push(`/books/${book.isbn}`);
  }

  if (!user || loading) {
    return null;
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
        <main className="max-w-xl mx-auto px-6 pt-12">
          <p className="text-sm text-[#526187]">Reading list not found.</p>
        </main>
      </div>
    );
  }

  const books = list.books || [];
  const totalPages = Math.max(1, Math.ceil(books.length / PAGE_SIZE));
  const startIndex = page * PAGE_SIZE;
  const visibleBooks = books.slice(startIndex, startIndex + PAGE_SIZE);
  const canPrev = page > 0;
  const canNext = page < totalPages - 1;

  return (
    <div className="min-h-screen bg-[#F7F9FC]">
      <Header
        user={user}
        setFormType={setFormType}
        handleLogout={handleLogout}
        compact
        showProfileButton={false}
      />

      <main className="max-w-xl mx-auto px-6 pt-10 pb-16">
        {/* title + visibility pill */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-extrabold text-[#14213D]">
            {list.name}
          </h1>

          <button
            onClick={handleToggleVisibility}
            disabled={toggling}
            className={`px-5 py-2 rounded-full text-sm font-semibold shadow-sm ${
              list.is_public
                ? "bg-white border border-[#FFD52E] text-[#856000]"
                : "bg-[#FFD52E] text-[#14213D]"
            }`}
          >
            {list.is_public ? "Public" : "Private"}
          </button>
        </div>

        {/* books card */}
        <section className="bg-white rounded-3xl border border-[#E4ECFF] shadow-[0_18px_40px_rgba(15,35,52,0.08)] overflow-hidden">
          {visibleBooks.length === 0 ? (
            <div className="px-6 py-8">
              <p className="text-sm text-[#74819A]">
                No books in this list yet.
              </p>
            </div>
          ) : (
            visibleBooks.map((book, index) => {
              const isLast = index === visibleBooks.length - 1;
              const rating =
                book.user_rating ??
                book.rating ??
                book.score ??
                book.my_rating ??
                null;

              return (
                <button
                  key={book.isbn ?? index}
                  type="button"
                  onClick={() => handleOpenBook(book)}
                  className={`w-full text-left px-6 py-5 flex items-center justify-between gap-4 hover:bg-[#F5F7FF] ${
                    !isLast ? "border-b border-[#E4ECFF]" : ""
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <BookIcon />
                    <div className="flex flex-col">
                      <span className="text-base font-semibold text-[#14213D]">
                        {book.book_title ?? book.title ?? "Untitled"}
                      </span>
                      <span className="text-sm text-[#74819A]">
                        {book.author ?? book.author_name ?? "Unknown author"}
                      </span>
                    </div>
                  </div>

                  <div className="text-lg font-semibold text-[#14213D] pr-1">
                    {rating != null ? rating : "-"}
                  </div>
                </button>
              );
            })
          )}

          {/* pagination row */}
          {books.length > PAGE_SIZE && (
            <div className="flex items-center justify-end gap-4 px-6 py-4">
              <button
                type="button"
                disabled={!canPrev}
                onClick={() => canPrev && setPage((p) => p - 1)}
                className="text-sm font-semibold text-[#1751FF] disabled:text-gray-300"
              >
                Previous
              </button>
              <span className="text-xs text-[#74819A]">
                Page {page + 1} of {totalPages}
              </span>
              <button
                type="button"
                disabled={!canNext}
                onClick={() => canNext && setPage((p) => p + 1)}
                className="flex items-center gap-1 text-sm font-semibold text-[#1751FF] disabled:text-gray-300"
              >
                Next <span>→</span>
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
