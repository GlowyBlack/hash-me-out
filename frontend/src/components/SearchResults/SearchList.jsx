"use client";

import { useState } from "react";

export default function SearchList({ results, hasSearched, query }) {
  const [showModal, setShowModal] = useState(false);

  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [isbn, setIsbn] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const hasQuery = query && query.trim().length > 0;
  const noResults = Array.isArray(results) && results.length === 0;

  // Open modal when user clicks "Request Book"
  const handleOpenModal = () => {
    setTitle(query || "");
    setAuthor("");
    setIsbn("");
    setNotes("");
    setShowModal(true);
  };

  const handleCloseModal = () => {
    if (submitting) return;
    setShowModal(false);
  };

  const submitRequest = async () => {
  try {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;

    if (!token) {
      alert("Please log in to request a book.");
      return;
    }

    setSubmitting(true);

    const res = await fetch("http://localhost:8000/requests/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
  title,
  book_title: title,  // for old schema if it exists
  author,
  isbn,
  notes,
}),

    });

    let data = null;
    try {
      data = await res.json();
    } catch {
      // no body
    }

        if (!res.ok) {
      console.log("Request error raw data:", data);

      let msg = "Error submitting request.";
      const detail = data?.detail;

      if (Array.isArray(detail) && detail.length > 0) {
        // include which field is the problem
        msg = detail
          .map((d) => `${d.loc?.join(".")}: ${d.msg}`)
          .join("\n");
      } else if (typeof detail === "string") {
        msg = detail;
      } else if (data) {
        msg = JSON.stringify(data);
      }

      alert(msg);
      return;
    }


    alert("Book request submitted!");
    setShowModal(false);
    setAuthor("");
    setIsbn("");
    setNotes("");
  } catch (err) {
    console.error("Request error:", err);
    alert("Error submitting request.");
  } finally {
    setSubmitting(false);
  }
};


  // 1) No search yet → show nothing
  if (!hasSearched || !hasQuery) {
    return null;
  }

  return (
    <>
      {/* 2) No results → show Request Book button */}
      {noResults && (
        <div className="mt-6 text-center">
          <p className="text-gray-700 mb-4">
            No books found for <span className="font-semibold">"{query}"</span>.
          </p>

          <button
            onClick={handleOpenModal}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition"
          >
            Request Book
          </button>
        </div>
      )}

      {/* 3) Results → show the list normally */}
      {!noResults && results && results.length > 0 && (
        <div className="mt-4 space-y-3">
          {results.map((book) => (
            <div
              key={book.isbn}
              className="p-3 bg-white shadow-sm rounded-md border hover:shadow-md transition text-sm"
            >
              <h2 className="text-lg font-bold text-gray-900">
                {book.book_title}
              </h2>
              <p className="text-gray-700">Author: {book.author}</p>
              <p className="text-gray-600 text-sm">ISBN: {book.isbn}</p>
            </div>
          ))}
        </div>
      )}

      {/* 4) Modal popup */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md space-y-4 shadow-lg">
            <h2 className="text-xl font-semibold">
              Request a new book for "{query}"
            </h2>

            <input
              placeholder="Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="border rounded px-3 py-2 w-full"
            />

            <input
              placeholder="Author"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className="border rounded px-3 py-2 w-full"
            />

            <input
              placeholder="ISBN"
              value={isbn}
              onChange={(e) => setIsbn(e.target.value)}
              className="border rounded px-3 py-2 w-full"
            />

            <textarea
              placeholder="Notes (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              rows={3}
            />

            <div className="flex justify-end gap-2 pt-2">
              <button
                className="px-3 py-2 border rounded"
                onClick={handleCloseModal}
                disabled={submitting}
              >
                Cancel
              </button>

              <button
                className="px-3 py-2 bg-blue-600 text-white rounded disabled:opacity-60"
                onClick={submitRequest}
                disabled={submitting}
              >
                {submitting ? "Submitting..." : "Submit Request"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
