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
    <div className="max-w-md mx-auto relative" ref={searchRef}>
      <form onSubmit={handleSearch} className="flex">
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2 border rounded-l-lg"
        />
        <button type="submit" className="bg-amber-200 px-4 rounded-r-lg font-semibold">
          Search
        </button>
      </form>

      <LiveSearchDropdown
        liveResults={liveResults}
        setSearch={setSearch}
      />

      {isTyping && (
        <p className="absolute left-0 mt-1 text-xs text-gray-500">Searching...</p>
      )}
    </div>
  );
}
