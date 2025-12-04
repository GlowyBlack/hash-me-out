"use client";

import { useState, useEffect, useRef } from "react";

import SearchBar from "../../components/SearchBar/SearchBar";
import Pagination from "../../components/SearchResults/Pagination";

export default function BooksAdmin() {
  // ============================
  // SEARCH STATE
  // ============================
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ============================
  // LIVE SEARCH STATE
  // ============================
  const [liveResults, setLiveResults] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  // ============================
  // PAGINATION
  // ============================
  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 6;

  const indexOfLast = currentPage * resultsPerPage;
  const indexOfFirst = indexOfLast - resultsPerPage;
  const currentResults = results.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(results.length / resultsPerPage);

  // ============================
  // EDIT MODAL
  // ============================
  const [selectedBook, setSelectedBook] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  // ============================
  // REF for click-outside closing
  // ============================
  const searchRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setLiveResults([]);
        setIsTyping(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // ----------------------------
  // FULL SEARCH
  // ----------------------------
  const handleSearch = async (e) => {
    e.preventDefault();
    setLiveResults([]);
    setIsTyping(false);

    if (!search.trim()) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const res = await fetch(
        `http://localhost:8000/books/search?query=${search}`
      );

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);

      setResults(data);
      setCurrentPage(1);
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  // ----------------------------
  // LIVE SEARCH
  // ----------------------------
  useEffect(() => {
    if (!search.trim()) {
      setLiveResults([]);
      return;
    }

    setIsTyping(true);

    const timeout = setTimeout(async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/books/live-search?query=${search}`
        );
        const data = await res.json();
        setLiveResults(data);
      } catch (err) {
        console.log(err);
      }
      setIsTyping(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, [search]);

  // ----------------------------
  // DELETE BOOK
  // ----------------------------
  async function deleteBook(isbn) {
    const token = localStorage.getItem("access_token");
    if (!confirm("Delete this book?")) return;

    const res = await fetch(`http://localhost:8000/books/${isbn}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      alert("Book deleted.");
      handleSearch(new Event("submit"));
    } else {
      alert("Failed to delete.");
    }
  }

  // ----------------------------
  // SAVE EDIT
  // ----------------------------
  async function saveEdit() {
    const token = localStorage.getItem("access_token");

    const res = await fetch(
      `http://localhost:8000/books/${selectedBook.isbn}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(selectedBook),
      }
    );

    const data = await res.json();

    if (res.ok) {
      alert("Book updated successfully.");
      setShowEditModal(false);
      handleSearch(new Event("submit"));
    } else {
      alert(data.detail || "Failed to update book.");
    }
  }

  // ======================================
  // RETURN UI
  // ======================================
  return (
    <div className="min-h-screen bg-gray-50 pt-24 pb-10 px-6">
      <h1 className="text-4xl font-bold text-gray-900 text-center">
        Books Manager
      </h1>

      {/* SEARCH BAR */}
      <div className="mt-10 max-w-3xl mx-auto">
        <SearchBar
          search={search}
          setSearch={setSearch}
          handleSearch={handleSearch}
          liveResults={liveResults}
          isTyping={isTyping}
          searchRef={searchRef}
        />
      </div>

      {/* RESULTS */}
      <div className="max-w-5xl mx-auto mt-10">
        {loading && <p className="text-center">Loading...</p>}
        {error && <p className="text-red-600 text-center">{error}</p>}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {currentResults.map((book) => (
            <div
              key={book.isbn}
              className="bg-white p-5 rounded-lg shadow border"
            >
              <h3 className="font-semibold text-lg">{book.book_title}</h3>
              <p className="text-gray-700">{book.author}</p>
              <p className="text-sm text-gray-500 mt-1">ISBN: {book.isbn}</p>

              <div className="flex gap-3 mt-5">
                <button
                  className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600"
                  onClick={() => {
                    setSelectedBook(book);
                    setShowEditModal(true);
                  }}
                >
                  Edit
                </button>

                <button
                  className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                  onClick={() => deleteBook(book.isbn)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          setCurrentPage={setCurrentPage}
        />
      </div>

      {/* EDIT MODAL */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center">
          <div className="bg-white p-6 rounded-lg w-[450px] shadow-xl">
            <h2 className="text-xl font-bold">Edit Book</h2>

            {Object.keys(selectedBook).map((field) => {
              if (field === "isbn") return null;
              return (
                <div key={field} className="mt-4">
                  <label className="font-semibold capitalize">
                    {field.replace(/_/g, " ")}
                  </label>
                  <input
                    className="border p-2 rounded w-full mt-1"
                    value={selectedBook[field] ?? ""}
                    onChange={(e) =>
                      setSelectedBook({
                        ...selectedBook,
                        [field]: e.target.value,
                      })
                    }
                  />
                </div>
              );
            })}

            <div className="flex justify-end gap-3 mt-6">
              <button
                className="px-3 py-1 rounded bg-gray-300"
                onClick={() => setShowEditModal(false)}
              >
                Cancel
              </button>

              <button
                className="px-4 py-1 rounded bg-blue-600 text-white"
                onClick={saveEdit}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
