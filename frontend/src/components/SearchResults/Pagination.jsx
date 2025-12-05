"use client";

export default function Pagination({
  currentPage,
  totalPages,
  setCurrentPage,
  ellipsisOpen,
  setEllipsisOpen,
  jumpPage,
  setJumpPage,
}) {
  if (totalPages <= 1) return null;

  const handleJump = () => {
    const pageNum = Number(jumpPage);
    if (pageNum >= 1 && pageNum <= totalPages) {
      setCurrentPage(pageNum);
      setJumpPage("");
      setEllipsisOpen(null);
    }
  };

  return (
    <div className="flex justify-center mt-6 space-x-2 select-none text-gray-700">

      {/* Prev */}
      <button
        disabled={currentPage === 1}
        onClick={() => setCurrentPage((p) => p - 1)}
        className={`px-3 py-1 rounded-md border text-sm text-gray-700
          ${currentPage === 1 ? "opacity-40 cursor-not-allowed" : "hover:bg-gray-100"}
        `}
      >
        Prev
      </button>

      {/* FIRST PAGE */}
      {currentPage > 3 && (
        <button
          className="px-3 py-1 border rounded-md text-sm hover:bg-gray-100 text-gray-700"
          onClick={() => setCurrentPage(1)}
        >
          1
        </button>
      )}

      {/* LEFT ELLIPSIS */}
      {currentPage > 4 && (
        <span className="px-2 text-gray-500">…</span>
      )}

      {/* SLIDING WINDOW */}
      {Array.from({ length: 5 }, (_, i) => {
        const page = currentPage - 2 + i;
        if (page < 1 || page > totalPages) return null;

        return (
          <button
            key={page}
            onClick={() => setCurrentPage(page)}
            className={`px-3 py-1 border rounded-md text-sm text-gray-700
              ${
                currentPage === page
                  ? "bg-yellow-300 border-yellow-400 font-semibold"
                  : "hover:bg-gray-100"
              }
            `}
          >
            {page}
          </button>
        );
      })}

      {currentPage < totalPages - 3 && (
        <span className="px-2 text-gray-500">…</span>
      )}
      {/* LAST PAGE */}
      {currentPage < totalPages - 2 && (
        <button
          className="px-3 py-1 border rounded-md text-sm hover:bg-gray-100 text-gray-700"
          onClick={() => setCurrentPage(totalPages)}
        >
          {totalPages}
        </button>
      )}

      {/* Next */}
      <button
        disabled={currentPage === totalPages}
        onClick={() => setCurrentPage((p) => p + 1)}
        className={`px-3 py-1 rounded-md border text-sm text-gray-700
          ${
            currentPage === totalPages
              ? "opacity-40 cursor-not-allowed"
              : "hover:bg-gray-100"
          }
        `}
      >
        Next
      </button>
    </div>
  );
}
