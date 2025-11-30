"use client";

export default function LiveSearchDropdown({ liveResults, setSearch }) {
  if (!liveResults || liveResults.length === 0) return null;

  return (
    <div className="absolute left-0 right-0 bg-white border shadow-md rounded-b-md mt-1 max-h-64 overflow-y-auto z-40">
      {liveResults.map((item) => (
        <div
          key={item.isbn}
          onClick={() => {
            setSearch(item.book_title);
          }}
          className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm"
        >
          <span className="font-semibold">{item.book_title}</span>
          <div className="text-gray-600">{item.author}</div>
        </div>
      ))}
    </div>
  );
}
