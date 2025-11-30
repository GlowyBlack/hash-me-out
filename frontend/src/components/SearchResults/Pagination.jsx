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
    <div className="flex justify-center mt-6 space-x-2 select-none">

      {/* Prev */}
      <button
        disabled={currentPage === 1}
        onClick={() => setCurrentPage((p) => p - 1)}
        className={`px-3 py-1 rounded-md border text-sm
          ${currentPage === 1 ? "opacity-40 cursor-not-allowed" : "hover:bg-gray-100"}
        `}
      >
        Prev
      </button>

      {/* FIRST PAGE */}
      {currentPage > 3 && (
        <button
          className="px-3 py-1 border rounded-md text-sm hover:bg-gray-100"
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
            className={`px-3 py-1 border rounded-md text-sm
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

      {/* RIGHT ELLIPSIS */}
      {/* {currentPage < totalPages - 3 && (
        <div className="relative">
          <button
            onClick={() =>
              setEllipsisOpen(ellipsisOpen === "right" ? null : "right")
            }
            className="px-2 text-gray-500 hover:text-black"
          >
            …
          </button>

          {ellipsisOpen === "right" && (
            <div className="absolute right-0 mt-1 bg-white border shadow-lg rounded-md p-3 w-32 z-50">
              <input
                type="number"
                min={1}
                max={totalPages}
                value={jumpPage}
                onChange={(e) => setJumpPage(e.target.value)}
                className="w-full px-2 py-1 border rounded text-sm"
                placeholder="Page #"
              />
              <button
                onClick={handleJump}
                className="mt-2 w-full bg-yellow-300 hover:bg-yellow-400 py-1 rounded text-sm"
              >
                Go
              </button>
            </div>
          )}
        </div>
      )} */}
      {currentPage < totalPages - 3 && (
        <span className="px-2 text-gray-500">…</span>
      )}
      {/* LAST PAGE */}
      {currentPage < totalPages - 2 && (
        <button
          className="px-3 py-1 border rounded-md text-sm hover:bg-gray-100"
          onClick={() => setCurrentPage(totalPages)}
        >
          {totalPages}
        </button>
      )}

      {/* Next */}
      <button
        disabled={currentPage === totalPages}
        onClick={() => setCurrentPage((p) => p + 1)}
        className={`px-3 py-1 rounded-md border text-sm
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
