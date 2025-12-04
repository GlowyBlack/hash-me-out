"use client";

import { useState } from "react";

export default function FilterModal({
  isOpen,
  onClose,
  onApply,
  initialFilters,
}) {
  const [author, setAuthor] = useState(initialFilters.author || "");
  const [genre, setGenre] = useState(initialFilters.genre || "");
  const [yearMin, setYearMin] = useState(initialFilters.year_min || "");
  const [yearMax, setYearMax] = useState(initialFilters.year_max || "");

  if (!isOpen) return null;

  function resetFilters() {
    setAuthor("");
    setGenre("");
    setYearMin("");
    setYearMax("");
  }

  function handleApply() {
    onApply({
      author,
      genre,
      year_min: yearMin || null,
      year_max: yearMax || null,
    });
    onClose();
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex justify-center items-center z-50">
      <div className="bg-white w-96 rounded-xl shadow-xl p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Filters</h2>
          <button onClick={onClose} className="text-gray-500 text-lg">✕</button>
        </div>

        {/* Author */}
        <label className="block mb-3">
          <span className="text-gray-700">Author</span>
          <input
            type="text"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 mt-1 text-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-400"
            placeholder="e.g., Stephen King"
          />
        </label>

        {/* Genre */}
        <label className="block mb-3">
          <span className="text-gray-700">Genre</span>
          <input
            type="text"
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 mt-1 text-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-400"
            placeholder="e.g., Fantasy"
          />
        </label>

        {/* Year range */}
        <div className="grid grid-cols-2 gap-4 mb-5">
          <label>
            <span className="text-gray-700">Year Min</span>
            <input
              type="number"
              value={yearMin}
              onChange={(e) => setYearMin(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 mt-1 text-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
          </label>

          <label>
            <span className="text-gray-700">Year Max</span>
            <input
              type="number"
              value={yearMax}
              onChange={(e) => setYearMax(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 mt-1 text-gray-700 focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
          </label>
        </div>

        {/* Buttons */}
        <div className="flex justify-between">
          <button
            onClick={resetFilters}
            className="px-4 py-2 text-gray-400 border rounded-lg "
          >
            Reset
          </button>

          <button
            onClick={handleApply}
            className="px-4 py-2 bg-yellow-400 rounded-lg font-semibold text-gray-600"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}
