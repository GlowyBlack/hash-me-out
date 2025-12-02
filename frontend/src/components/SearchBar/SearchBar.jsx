"use client";

import LiveSearchDropdown from "./LiveSearchDropdown";

export default function SearchBar({
  search,
  setSearch,
  handleSearch,
  liveResults,
  isTyping,
  searchRef
}) {
  return (
    <div className="max-w-2xl w-full mx-auto relative" ref={searchRef}>
      <form onSubmit={handleSearch} className="flex w-full">
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg bg-gray-50 focus:ring-2 focus:ring-yellow-400 text-gray-900"
        />
        <button
          type="submit"
          className="bg-yellow-400 hover:bg-yellow-500 px-6 rounded-r-lg font-semibold"
        >
          Search
        </button>
      </form>

      <LiveSearchDropdown liveResults={liveResults} setSearch={setSearch} />

      {isTyping && (
        <p className="absolute left-0 mt-1 text-xs text-gray-500">
          Searching...
        </p>
      )}
    </div>
  );
}