"use client";

import { useRouter } from "next/navigation";
import { toTitleCase } from "@/utils/textHelpers";


export default function SimilarBooksSidebar({ similarBooks }) {
  const router = useRouter();

  if (!similarBooks || similarBooks.length === 0) {
    return null;
  }

  return (
    <aside className="w-full lg:w-80 bg-white border rounded-3xl shadow-md p-5 h-fit">
      <h2 className="text-lg font-semibold mb-4 text-gray-900">
        Similar Books
      </h2>

      <div className="grid grid-cols-2 gap-4">
        {similarBooks.map((b) => (
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
