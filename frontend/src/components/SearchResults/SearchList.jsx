"use client";

import { useRouter } from "next/navigation";
// import { dedupeBooks } from "@/utils/dedupeBooks";

export default function SearchList({ results }) {
  const router = useRouter();


  return (
    <div className="mt-4 space-y-3">
      {results.map((book) => (
        <div 
          key={book.isbn}
          onClick={() => router.push(`/books/${book.isbn}`)}
          className="p-3 bg-white shadow-sm rounded-md border hover:shadow-md transition text-sm"
        >
          <h2 className="text-lg font-bold text-gray-900">{book.book_title}</h2>
          <p className="text-gray-700">Author: {book.author}</p>
          <p className="text-gray-600 text-sm">ISBN: {book.isbn}</p>
        </div>
      ))}
    </div>
  );
}
