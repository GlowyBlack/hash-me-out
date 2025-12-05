"use client";

import React, { useCallback } from "react";
import useEmblaCarousel from "embla-carousel-react";
import Autoplay from "embla-carousel-autoplay";
import Link from "next/link";

export default function RecommendedForYou({ books }) {
  const autoplayOptions = {
    delay: 3500,
    stopOnMouseEnter: true,
    stopOnInteraction: false,
  };

  const [emblaRef, emblaApi] = useEmblaCarousel(
    {
      loop: true,
      align: "start",
      dragFree: false,
    },
    [Autoplay(autoplayOptions)]
  );

  // Manual next / prev
  const scrollPrev = useCallback(() => emblaApi && emblaApi.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi && emblaApi.scrollNext(), [emblaApi]);

  return (
    <div className="px-6 mt-10">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          Recommended for You
        </h2>

        <div className="flex gap-3">
          <button
            onClick={scrollPrev}
            className="px-3 py-1 border rounded-lg bg-white hover:bg-gray-100"
          >
            ◀
          </button>
          <button
            onClick={scrollNext}
            className="px-3 py-1 border rounded-lg bg-white hover:bg-gray-100"
          >
            ▶
          </button>
        </div>
      </div>

      {/* Carousel wrapper */}
      <div className="overflow-hidden" ref={emblaRef}>
        <div className="flex gap-6" style={{ marginLeft: 0 }}>
          {books.map((b) => (
            <Link
              key={b.isbn}
              href={`/books/${b.isbn}`}
              className="flex-none w-56 bg-white border rounded-xl shadow p-3 transition-opacity duration-700 hover:opacity-80"
            >
              <img
                src={b.image_url_l || b.image_url_m || b.image_url_s}
                className="w-full h-44 object-contain rounded-md mb-2"
                alt={b.title}
              />

              <p className="text-sm font-semibold line-clamp-2 text-gray-900">
                {b.title}
              </p>
              <p className="text-xs text-gray-600">{b.author}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
