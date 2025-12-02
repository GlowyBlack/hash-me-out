"use client";

import { useState } from "react";

export default function BookDetailPage({ book, avgRating, initialReviews }) {
  // Backend gives: book_title, author, year_of_publication, publisher, image_url_l, isbn
  const displayTitle = book.book_title;
  const displayYear = book.year_of_publication;
  const displayPublisher = book.publisher;
  const displayAuthor = book.author;
  const coverUrl = book.image_url_l || book.image_url_m || book.image_url_s;

  // Use backend avg rating if we have it
  const initialAvgRating = avgRating?.avg_rating ?? 0;
  const initialRatingCount = avgRating?.count ?? 0;

  // Reviews list comes from backend
  const [reviews, setReviews] = useState(initialReviews || []);

  // User rating and review (simple version)
  const [userRating, setUserRating] = useState(null);
  const [userComment, setUserComment] = useState("");
  const [isEditing, setIsEditing] = useState(true);
  const [saving, setSaving] = useState(false);

  const API_BASE =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  async function handleSave() {
    try {
      setSaving(true);

      // 1) Save rating
      if (userRating !== null) {
      await fetch(`${API_BASE}/ratings/books/${book.isbn}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ rating: userRating }),
      });
    }

      // 2) Save review
      const reviewRes = await fetch(
        `${API_BASE}/reviews?isbn=${encodeURIComponent(book.isbn)}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({ comment: userComment }),
        }
      );

      if (!reviewRes.ok) {
        const err = await reviewRes.json().catch(() => ({}));
        console.error("Review error", err);
        alert("Could not save review. Check console for details.");
      } else {
        const newReview = await reviewRes.json();
        setReviews((prev) => [newReview, ...prev]);
        setIsEditing(false);
      }
    } catch (e) {
      console.error(e);
      alert("Something went wrong while saving.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-white text-slate-900">
      {/* Top nav */}
      <header className="sticky top-0 z-10 bg-white border-b border-slate-200 px-8 md:px-12 py-4 flex items-center justify-between">
        <div className="text-[1.05rem] font-bold text-[#023147]">
          Home
        </div>
        <div className="flex items-center gap-3">
          <button className="rounded-full border border-slate-300 bg-white text-slate-800 text-sm font-semibold px-4 py-2 hover:bg-slate-50 transition">
            Profile
          </button>
          <button className="rounded-full border border-[#ffb803] bg-[#ffb803] text-slate-900 text-sm font-semibold px-4 py-2 shadow-sm hover:bg-[#f5a800] hover:border-[#f5a800] transition">
            Logout
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="px-6 md:px-12 py-8 md:py-12">
        <section className="max-w-5xl mx-auto flex flex-col lg:flex-row gap-8 lg:gap-10">
          {/* LEFT: Book info card */}
          <div className="w-full lg:max-w-xs bg-white border border-slate-200 rounded-3xl shadow-lg p-6 flex flex-col">
            <div className="flex justify-center mb-5">
              {coverUrl ? (
                <img
                  src={coverUrl}
                  alt={displayTitle}
                  className="w-48 h-auto rounded-xl shadow-xl object-cover"
                />
              ) : (
                <div className="w-48 h-64 rounded-xl flex items-center justify-center bg-slate-100 text-slate-500 text-sm">
                  No cover
                </div>
              )}
            </div>

            <div>
              <h1 className="text-xl md:text-2xl font-semibold text-slate-900 mb-1">
                {displayTitle}
              </h1>
              <p className="text-slate-600 font-medium mb-4">
                by {displayAuthor}
              </p>

              <div className="text-sm text-slate-700 space-y-1.5">
                <div>
                  <span className="font-semibold text-[#023147] mr-1">
                    Year:
                  </span>
                  {displayYear || "N/A"}
                </div>
                <div>
                  <span className="font-semibold text-[#023147] mr-1">
                    Publisher:
                  </span>
                  {displayPublisher || "N/A"}
                </div>
                <div>
                  <span className="font-semibold text-[#023147] mr-1">
                    ISBN:
                  </span>
                  {book.isbn}
                </div>
              </div>

              {/* Genres can go here later if you add them to the API */}
              {/* <div className="mt-4 flex flex-wrap gap-2">
                {book.genres?.map((g) => (
                  <span
                    key={g}
                    className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-700"
                  >
                    {g}
                  </span>
                ))}
              </div> */}
            </div>
          </div>

          {/* RIGHT: Rating + review editor + reviews list */}
          <div className="flex-1 flex flex-col gap-5">
            {/* Rating card */}
            <div className="bg-white border border-slate-200 rounded-2xl shadow-md p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base md:text-lg font-semibold text-slate-900">
                  Your Rating
                </h2>
                <div className="inline-flex items-center rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
                  Avg: {initialAvgRating.toFixed(1)} / 10
                  {initialRatingCount > 0 && (
                    <span className="ml-1 text-[0.7rem] text-amber-900">
                      ({initialRatingCount})
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-3">
                <label className="flex-1 flex items-center gap-3 text-xs text-slate-600">
                  <span>0</span>

                  <input
                    type="range"
                    min="0"
                    max="10"
                    value={userRating ?? 0}   // visual default
                    onChange={(e) => {
                      // First interaction activates rating mode
                      setUserRating(Number(e.target.value));
                    }}
                    className={`flex-1 
                      ${userRating === null 
                        ? "opacity-40 cursor-pointer accent-slate-300"   // GREYED OUT
                        : "accent-[#ffb803]"                             // ACTIVE
                      }
                    `}
                  />

                  <span>10</span>
                </label>

                <span className="min-w-[80px] text-right font-semibold text-[#023147]">
                  {userRating === null ? "No rating" : `${userRating}/10`}
                </span>
              </div>
            </div>

            {/* Review editor */}
            <div className="bg-white border border-slate-200 rounded-2xl shadow-md p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-base md:text-lg font-semibold text-slate-900">
                  Your Review
                </h2>
                {!isEditing && (
                  <button
                    className="rounded-full border border-slate-300 bg-white text-xs font-medium px-3 py-1 hover:bg-slate-50 transition"
                    onClick={() => setIsEditing(true)}
                  >
                    Edit
                  </button>
                )}
              </div>

              <textarea
                className="w-full min-h-[110px] resize-y rounded-xl border border-slate-300 px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-300 focus:border-amber-400 disabled:bg-slate-50 disabled:text-slate-500"
                value={userComment}
                onChange={(e) => setUserComment(e.target.value)}
                disabled={!isEditing}
                maxLength={500}
                placeholder="Write your thoughts about this book..."
              />

              <div className="mt-2 flex items-center justify-between text-xs">
                <span className="text-slate-500">
                  {userComment.length}/500
                </span>
                <button
                  className="rounded-full border border-[#ffb803] bg-[#ffb803] text-[0.8rem] font-semibold px-4 py-1.5 text-slate-900 shadow-sm hover:bg-[#f5a800] hover:border-[#f5a800] disabled:opacity-60 disabled:cursor-default transition"
                  onClick={handleSave}
                  disabled={!isEditing || saving}
                >
                  {saving ? "Saving..." : "Save Review"}
                </button>
              </div>
            </div>

            {/* Reviews list */}
            <section className="mt-1">
              <h2 className="text-base md:text-lg font-semibold text-slate-900 mb-2">
                Reviews
              </h2>
              {reviews.length === 0 && (
                <p className="text-sm text-slate-500">
                  No reviews yet. Be the first to review this book!
                </p>
              )}

              <div className="space-y-3 mt-2">
                {reviews.map((r) => (
                  <article
                    key={r.review_id}
                    className="bg-white border border-slate-200 rounded-xl px-4 py-3"
                  >
                    <div className="flex items-baseline justify-between mb-1.5">
                      <div className="flex items-baseline gap-2">
                        <span className="text-sm font-semibold text-slate-900">
                          User #{r.user_id}
                        </span>
                        <span className="text-[0.7rem] text-slate-400">
                          {new Date(r.time).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-700 whitespace-pre-line">
                      {r.comment}
                    </p>
                  </article>
                ))}
              </div>
            </section>
          </div>
        </section>
      </main>
    </div>
  );
}
