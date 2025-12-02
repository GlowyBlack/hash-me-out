// src/components/bookDetails.jsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Header from "./Header";
import AuthPopup from "./AuthPopup/AuthPopup";
import Pagination from "./SearchResults/Pagination";

export default function BookDetailPage({ book, avgRating, initialReviews }) {
  const router = useRouter();

  // Backend gives: book_title, author, year_of_publication, publisher, image_url_l, isbn
  const displayTitle = book.book_title;
  const displayYear = book.year_of_publication;
  const displayPublisher = book.publisher;
  const displayAuthor = book.author;
  const coverUrl = book.image_url_l || book.image_url_m || book.image_url_s;

  // Average rating from backend
  const initialAvgRating = avgRating?.avg_rating ?? 0;
  const initialRatingCount = avgRating?.count ?? 0;

  // Reviews list from backend
  const [reviews, setReviews] = useState(initialReviews || []);

  // User rating and review (rating optional)
  const [userRating, setUserRating] = useState(null);
  const [userComment, setUserComment] = useState("");
  const [isEditing, setIsEditing] = useState(true);
  const [saving, setSaving] = useState(false);

  // Auth state (same pattern as HomePage)
  const [user, setUser] = useState(null);
  const [formType, setFormType] = useState(null); // "login" | "register" | null

  // Pagination for reviews
  const [currentReviewPage, setCurrentReviewPage] = useState(1);
  const [ellipsisOpen, setEllipsisOpen] = useState(null);
  const [jumpPage, setJumpPage] = useState("");

  const reviewsPerPage = 5;
  const totalReviewPages = Math.ceil(reviews.length / reviewsPerPage);
  const indexOfLastReview = currentReviewPage * reviewsPerPage;
  const indexOfFirstReview = indexOfLastReview - reviewsPerPage;
  const currentReviews = reviews.slice(indexOfFirstReview, indexOfLastReview);

  const API_BASE =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  // Load user from token (same as HomePage)
  useEffect(() => {
    const token = typeof window !== "undefined"
      ? localStorage.getItem("access_token")
      : null;

    if (token) {
      try {
        const decoded = JSON.parse(atob(token.split(".")[1]));
        setUser(decoded);
      } catch (e) {
        console.error("Failed to decode token", e);
      }
    }
  }, []);

  // Called by AuthPopup when login/register succeeds
  const handleLoginSuccess = () => {
    setFormType(null);
    const token = localStorage.getItem("access_token");
    if (token) {
      try {
        const decoded = JSON.parse(atob(token.split(".")[1]));
        setUser(decoded);
      } catch (e) {
        console.error("Failed to decode token", e);
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/");
  };

  const goToProfile = () => {
    router.push("/profile");
  };

  async function handleSave() {
    // Not logged in: open login/register instead of calling the API
    if (!user) {
      // You can start with "login" instead if you prefer
      setFormType("register");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      setFormType("login");
      return;
    }

    // Optional: avoid obvious backend error on too-short comment
    if (!userComment || userComment.trim().length < 8) {
      alert("Please write at least 8 characters for your review.");
      return;
    }

    try {
      setSaving(true);

      // 1) Save rating (only if user moved the slider)
      if (userRating !== null) {
        const ratingRes = await fetch(
          `${API_BASE}/ratings/books/${book.isbn}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            credentials: "include",
            body: JSON.stringify({ rating: userRating }),
          }
        );

        if (!ratingRes.ok) {
          console.error(
            "Rating error",
            await ratingRes.json().catch(() => ({}))
          );
          // Do not block review if rating fails
        }
      }

      // 2) Save review
      const reviewRes = await fetch(
        `${API_BASE}/reviews?isbn=${encodeURIComponent(book.isbn)}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
          body: JSON.stringify({ comment: userComment }),
        }
      );

      if (!reviewRes.ok) {
        const err = await reviewRes.json().catch(() => ({}));
        console.error("Review error", err);

        if (reviewRes.status === 401) {
          setUser(null);
          setFormType("login");
          alert("Please log in to post a review.");
          return;
        }

        // Handle structured error messages from backend if present
        if (err?.detail?.message) {
          alert(err.detail.message);
        } else if (typeof err.detail === "string") {
          alert(err.detail);
        } else {
          alert("Could not save review.");
        }

        return;
      }

      const newReview = await reviewRes.json();
      // Prepend new review
      setReviews((prev) => [newReview, ...prev]);
      setIsEditing(false);
      // Reset to first page so user sees their review
      setCurrentReviewPage(1);
    } catch (e) {
      console.error(e);
      alert("Something went wrong while saving.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="relative min-h-screen bg-gray-50 text-slate-900">
      {/* Shared header with functional auth */}
      <Header
        user={user}
        setFormType={setFormType}
        handleLogout={handleLogout}
        goToProfile={goToProfile}
      />

      {/* Login/Register popup */}
      <AuthPopup
        formType={formType}
        setFormType={setFormType}
        handleLoginSuccess={handleLoginSuccess}
      />

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

              {/* Genres can go here later when backend exposes them */}
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
                    value={userRating ?? 0} // visual default
                    onChange={(e) => {
                      setUserRating(Number(e.target.value));
                    }}
                    className={`flex-1 ${
                      userRating === null
                        ? "opacity-40 cursor-pointer accent-slate-300"
                        : "accent-[#ffb803]"
                    }`}
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
                maxLength={750}
                placeholder="Write your thoughts about this book..."
              />
              {!user && (
                <p className="mt-1 text-sm text-red-500">
                  You must be logged in to post a review.
                </p>
              )}


              <div className="mt-2 flex items-center justify-between text-xs">
                <span className="text-slate-500">
                  {userComment.length}/750
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

            {/* Reviews list + pagination */}
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
                {currentReviews.map((r) => (
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

              <Pagination
                currentPage={currentReviewPage}
                totalPages={totalReviewPages}
                setCurrentPage={setCurrentReviewPage}
                ellipsisOpen={ellipsisOpen}
                setEllipsisOpen={setEllipsisOpen}
                jumpPage={jumpPage}
                setJumpPage={setJumpPage}
              />
            </section>
          </div>
        </section>
      </main>
    </div>
  );
}
