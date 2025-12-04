"use client";
import { useRouter } from "next/navigation";

export default function LiveSearchDropdown({ liveResults, setSearch }) {
    const router = useRouter();
  if (!liveResults || liveResults.length === 0) return null;

  return (
    <div className="absolute left-0 right-0 bg-white border shadow-md rounded-b-md mt-1 max-h-64 overflow-y-auto z-40">
      {liveResults.map((item) => (
        <div
          key={item.isbn}
          onClick={() =>  router.push(`/books/${item.isbn}`)}
          className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm"
        >
          <span className="font-semibold text-gray-900">{item.book_title}</span>
          <div className="text-gray-600">{item.author}</div>
        </div>
      ))}
    </div>
  );
}
