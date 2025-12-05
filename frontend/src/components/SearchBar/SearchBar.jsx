"use client";
import { useEffect } from "react";
import LiveSearchDropdown from "./LiveSearchDropdown";

export default function SearchBar({
  search,
  setSearch,
  handleSearch,
  liveResults,
  liveLoading,
  isTyping,
  searchRef,
  onOpenFilters,  
  setLiveResults, 
}) {
  useEffect(() => {
    function handleClickOutside(event) {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        // Clear live results → hides dropdown completely
        setLiveResults([]);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [searchRef, setLiveResults]);

  return (
    <div className="max-w-2xl w-full mx-auto relative" ref={searchRef}>
      <form onSubmit={handleSearch} className="flex items-center w-full space-x-2">
        {/* SEARCH INPUT */}
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 
                     focus:ring-2 focus:ring-yellow-400 text-gray-900"
        />

        {/* SEARCH BUTTON */}
        <button
          type="submit"
          className="bg-yellow-400 hover:bg-yellow-500 px-6 py-2 rounded-lg font-semibold shadow-sm"
        >
          Search
        </button>

        {/* FILTER BUTTON */}
        <button
          type="button"
          onClick={onOpenFilters}
          className="px-4 py-2 border border-gray-300 bg-white rounded-lg shadow-sm 
                     hover:bg-gray-100 text-gray-700"
        >
          Filters
        </button>
      </form>

      {/* LIVE SEARCH RESULT DROPDOWN */}
      <LiveSearchDropdown
        liveResults = {liveResults}
        liveLoading = {liveLoading}
        search = {search}
        onRequestClick={() => console.log("Open request modal soon")}
      />
      {isTyping && (
        <p className="absolute left-0 mt-1 text-xs text-gray-500">
          Searching...
        </p>
      )}
    </div>
  );
}
