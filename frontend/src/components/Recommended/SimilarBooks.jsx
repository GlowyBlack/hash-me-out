"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { toTitleCase } from "@/utils/textHelpers";

export default function SimilarBooksSidebar({ similarBooks }) {
  const router = useRouter();

  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState(true);

  const PAGE_SIZE = 4;
  const INTERVAL = 3500;
  const CLICK_PAUSE = 5000; // pause for 5 seconds after manual click

  const isPaused = useRef(false);
  const pauseTimeout = useRef(null);

  if (!similarBooks || similarBooks.length === 0) return null;

  /* -------------------------
      AUTO-ROTATION TIMER
     ------------------------- */
  useEffect(() => {
    const id = setInterval(() => {
      if (!isPaused.current) {
        nextSlide(true); // true = auto mode
      }
    }, INTERVAL);

    return () => clearInterval(id);
  }, [similarBooks.length]);

  /* -------------------------
      PAUSE HANDLING
     ------------------------- */
  const pauseAfterClick = () => {
    isPaused.current = true;

    if (pauseTimeout.current) {
      clearTimeout(pauseTimeout.current);
    }

    pauseTimeout.current = setTimeout(() => {
      isPaused.current = false;
    }, CLICK_PAUSE);
  };

  /* -------------------------
      BOOK SLICING (WITH WRAP)
     ------------------------- */
  const getVisibleBooks = () => {
    const end = index + PAGE_SIZE;
    if (end <= similarBooks.length) return similarBooks.slice(index, end);

    return [
      ...similarBooks.slice(index),
      ...similarBooks.slice(0, end - similarBooks.length),
    ];
  };

  const visibleBooks = getVisibleBooks();

  /* -------------------------
      ANIMATED SLIDE FUNCTIONS
     ------------------------- */
  const nextSlide = (auto = false) => {
    if (!auto) pauseAfterClick();

    setFade(false);
    setTimeout(() => {
      setIndex((prev) => (prev + PAGE_SIZE) % similarBooks.length);
      setFade(true);
    }, 250);
  };

  const prevSlide = () => {
    pauseAfterClick();

    setFade(false);
    setTimeout(() => {
      setIndex((prev) =>
        (prev - PAGE_SIZE + similarBooks.length) % similarBooks.length
      );
      setFade(true);
    }, 250);
  };

  return (
    <aside className="w-full lg:w-80 bg-white border rounded-3xl shadow-md p-5 h-fit">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Similar Books</h2>

        {/* Prev / Next */}
        <div className="flex gap-2">
          <button
            onClick={() => prevSlide()}
            className="px-2 py-1 rounded-md bg-gray-200 hover:bg-gray-300 transition"
          >
            ◀
          </button>
          <button
            onClick={() => nextSlide(false)}
            className="px-2 py-1 rounded-md bg-gray-200 hover:bg-gray-300 transition"
          >
            ▶
          </button>
        </div>
      </div>

      {/* Pause on Hover */}
      <div
        onMouseEnter={() => (isPaused.current = true)}
        onMouseLeave={() => (isPaused.current = false)}
        className={`grid grid-cols-2 gap-4 transition-opacity duration-500 ${
          fade ? "opacity-100" : "opacity-0"
        }`}
      >
        {visibleBooks.map((b) => (
          <div
            key={b.isbn}
            onClick={() => router.push(`/books/${b.isbn}`)}
            className="cursor-pointer bg-gray-50 hover:bg-gray-100 border rounded-xl p-3 shadow-sm transition"
          >
            <img
              src={b.image_url_m || b.image_url_s}
              alt={toTitleCase(b.title)}
              className="w-full h-40 object-cover rounded-md mb-2"
            />
            <h3 className="text-sm font-semibold text-gray-800 line-clamp-2">
              {b.title}
            </h3>
          </div>
        ))}
      </div>
    </aside>
  );
}
