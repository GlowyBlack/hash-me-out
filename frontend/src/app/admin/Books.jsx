"use client";

import { useState } from "react";

export default function AdminBooksPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Edit/Delete modal state
  const [editModal, setEditModal] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [currentBook, setCurrentBook] = useState(null);

  // ===========================
  // SEARCH BOOKS
  // ===========================
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");

    try {
      const res = await fetch(
        `http://localhost:8000/books/search?query=${encodeURIComponent(query)}`
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Error fetching books");
      setResults(data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  // ===========================
  // EDIT BOOK
  // ===========================
  const openEditModal = (book) => {
    setCurrentBook({ ...book, originalIsbn: book.isbn });
    setEditModal(true);
  };

  const closeEditModal = () => setEditModal(false);

  const submitEdit = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        alert("You must be logged in to edit books.");
        return;
      }

      const res = await fetch(
        `http://localhost:8000/books/${currentBook.originalIsbn}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            book_title: currentBook.book_title,
            author: currentBook.author,
            isbn: currentBook.isbn,
          }),
        }
      );

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        alert("Error updating book: " + JSON.stringify(data));
        return;
      }

      alert("Book updated successfully");
      closeEditModal();
      handleSearch(new Event("submit"));
    } catch (err) {
      alert("Could not update book");
    }
  };

  // ===========================
  // DELETE BOOK
  // ===========================
  const openDeleteModal = (book) => {
    setCurrentBook(book);
    setDeleteModal(true);
  };

  const closeDeleteModal = () => setDeleteModal(false);

  const confirmDelete = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        alert("You must be logged in to delete books.");
        return;
      }

      const res = await fetch(
        `http://localhost:8000/books/${currentBook.isbn}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await res.json().catch(() => null);

      if (!res.ok) {
        alert("Error deleting book: " + JSON.stringify(data));
        return;
      }

      alert("Book deleted successfully");
      closeDeleteModal();
      handleSearch(new Event("submit"));
    } catch (err) {
      alert("Could not delete book");
    }
  };

  // ===========================
  // PAGE UI
  // ===========================
  return (
    <div className="min-h-screen bg-gray-50 pt-24 pb-10 px-6">
      <h1 className="text-2xl font-bold mb-4">
        Manage Books
      </h1>

      {/* SEARCH */}
      <form
        onSubmit={handleSearch}
        className="mt-8 max-w-3xl mx-auto flex gap-2"
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title, author, etc."
          className="flex-1 border rounded px-3 py-2"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-yellow-400 text-gray-900 font-bold rounded-xl hover:bg-yellow-500 transition-colors"
        >
          Search
        </button>
      </form>

      {/* RESULTS */}
      <div className="mt-6 space-y-4 max-w-4xl mx-auto">
        {loading && <p className="text-center">Loading...</p>}
        {error && <p className="text-red-600 text-center">{error}</p>}

        {results.map((book) => (
          <div
            key={book.isbn}
            className="p-4 bg-white shadow-sm rounded-md border flex justify-between items-center"
          >
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                {book.book_title}
              </h2>
              <p className="text-gray-700">Author: {book.author}</p>
              <p className="text-gray-600 text-sm">ISBN: {book.isbn}</p>
            </div>

            <div className="flex gap-2">
              <button
                className="px-3 py-1 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded"
                onClick={() => openEditModal(book)}
              >
                Edit
              </button>

              <button
                className="px-3 py-1 bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-bold rounded"
                onClick={() => openDeleteModal(book)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* EDIT MODAL */}
      {editModal && currentBook && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md space-y-4 shadow-lg">
            <h2 className="text-xl font-semibold">Edit Book</h2>
            <input
              value={currentBook.book_title}
              onChange={(e) =>
                setCurrentBook({ ...currentBook, book_title: e.target.value })
              }
              className="border rounded px-3 py-2 w-full"
            />
            <input
              value={currentBook.author}
              onChange={(e) =>
                setCurrentBook({ ...currentBook, author: e.target.value })
              }
              className="border rounded px-3 py-2 w-full"
            />
            <input
              value={currentBook.isbn}
              onChange={(e) =>
                setCurrentBook({ ...currentBook, isbn: e.target.value })
              }
              className="border rounded px-3 py-2 w-full"
            />
            <div className="flex justify-end gap-2 pt-2">
              <button className="px-3 py-2 border rounded" onClick={closeEditModal}>
                Cancel
              </button>
              <button
                className="px-3 py-2 bg-blue-600 text-white rounded"
                onClick={submitEdit}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DELETE MODAL */}
      {deleteModal && currentBook && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md space-y-4 shadow-lg">
            <h2 className="text-xl font-semibold text-red-600">Delete Book?</h2>
            <p>
              Are you sure you want to delete <strong>{currentBook.book_title}</strong>?
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button className="px-3 py-2 border rounded" onClick={closeDeleteModal}>
                Cancel
              </button>
              <button
                className="px-3 py-2 bg-red-600 text-white rounded"
                onClick={confirmDelete}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
