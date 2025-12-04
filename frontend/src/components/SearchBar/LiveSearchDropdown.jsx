"use client";
import { useRouter } from "next/navigation";

export default function LiveSearchDropdown({ liveResults, liveLoading, search, saerchRef }) {
  const router = useRouter();

  const query = (search || "").trim();
  const showDropdown =
    query.length > 0 && (liveLoading || liveResults.length > 0);


  if (!showDropdown) return null;

  return (
    <div className="absolute left-0 right-0 bg-white border shadow-md rounded-b-md mt-1 max-h-64 overflow-y-auto z-40">

      {/* Loading State */}
      {liveLoading && (
        <div className="px-3 py-3 text-gray-500 text-sm">
          Searching...
        </div>
      )}

      {/* Results */}
      {!liveLoading && liveResults.length > 0 && (
        <>
          {liveResults.map((item) => (
            <div
              key={item.isbn}
              onClick={() => router.push(`/books/${item.isbn}`)}
              className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm"
            >
              <span className="font-semibold text-gray-900">
                {item.book_title}
              </span>
              <div className="text-gray-600 text-xs">{item.author}</div>
            </div>
          ))}
        </>
      )}

      {/* No Results */}
      {!liveLoading && liveResults.length === 0 && (
        <div className="px-3 py-4 text-gray-900 text-sm cursor-pointer">
          <div 
          onClick={() => alert("Request flow coming soon!")}>No match found. Click to Request</div>
        </div>
      )}

    </div>
  );
}
