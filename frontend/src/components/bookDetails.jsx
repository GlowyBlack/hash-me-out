"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Header from "./Header";
import AuthPopup from "./AuthPopup/AuthPopup";
import Pagination from "./SearchResults/Pagination";

export default function BookDetailPage({ book, avgRating, initialReviews }) {
  const router = useRouter();

  const displayTitle = book.book_title;
  const displayYear = book.year_of_publication;
  const displayPublisher = book.publisher;
  const displayAuthor = book.author;
  const coverUrl = book.image_url_l || book.image_url_m || book.image_url_s;

  const initialAvgRating = avgRating?.avg_rating ?? 0;
  const initialRatingCount = avgRating?.count ?? 0;

  const [reviews, setReviews] = useState(initialReviews || []);

  const [userRating, setUserRating] = useState(null);
  const [userComment, setUserComment] = useState("");
  const [isEditing, setIsEditing] = useState(true);
  const [saving, setSaving] = useState(false);

  const [user, setUser] = useState(null);
  const [formType, setFormType] = useState(null); 

  const [myReviewId, setMyReviewId] = useState(null);

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

  useEffect(() => {
    const token =
      typeof window !== "undefined"
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

  useEffect(() => {
    async function fetchReviews() {
      try {
        const res = await fetch(
          `${API_BASE}/reviews/${encodeURIComponent(book.isbn)}`,
          { cache: "no-store" }
        );
        if (!res.ok) {
          console.warn("Could not load reviews for", book.isbn);
          return;
        }
        const list = await res.json();
        const safeList = Array.isArray(list) ? list : [];
        setReviews(safeList);

        if (user && safeList.length > 0) {
          const mine = safeList.find((r) => r.user_id === user.id);
          if (mine) {
            setMyReviewId(mine.review_id);
            setUserComment(mine.comment);
            setIsEditing(false);
          }
        }
      } catch (e) {
        console.error("Error fetching reviews", e);
      }
    }

    fetchReviews();
  }, [API_BASE, book.isbn, user?.id]);

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
    if (!user) {
      setFormType("register");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      setFormType("login");
      return;
    }

    if (!userComment || userComment.trim().length < 8) {
      alert("Please write at least 8 characters for your review.");
      return;
    }

    try {
      setSaving(true);

      if (userRating !== null) {
        const ratingRes = await fetch(
          `${API_BASE}/ratings/books/${book.isbn}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ rating: userRating }),
          }
        );

        if (!ratingRes.ok) {
          const ratingErr = await ratingRes
            .json()
            .catch(() => ({ detail: "No JSON body" }));
          console.error(
            "Rating error",
            ratingRes.status,
            ratingRes.statusText,
            ratingErr
          );
        }
      }

      let reviewRes;
      if (myReviewId) {
        reviewRes = await fetch(`${API_BASE}/reviews/${myReviewId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ comment: userComment }),
        });
      } else {
        reviewRes = await fetch(
          `${API_BASE}/reviews/?isbn=${encodeURIComponent(book.isbn)}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ comment: userComment }),
          }
        );
      }

      if (!reviewRes.ok) {
        const err = await reviewRes.json().catch(() => ({}));
        console.error(
          "Review error (non-ok response)",
          reviewRes.status,
          reviewRes.statusText,
          err
        );

        if (reviewRes.status === 401) {
          setUser(null);
          setFormType("login");
          alert("Please log in to post a review.");
          return;
        }

        if (err?.detail?.message) {
          alert(err.detail.message);
        } else if (typeof err.detail === "string") {
          alert(err.detail);
        } else {
          alert("Could not save review.");
        }
        return;
      }

      let savedReview = null;
      try {
        savedReview = await reviewRes.json();
      } catch (jsonErr) {
        console.warn(
          "Review response had no JSON body (likely 204). Will refetch reviews.",
          jsonErr
        );
      }

      if (savedReview) {
        if (myReviewId) {
          setReviews((prev) =>
            prev.map((r) =>
              r.review_id === savedReview.review_id ? savedReview : r
            )
          );
        } else {
          setReviews((prev) => [savedReview, ...prev]);
          setMyReviewId(savedReview.review_id);
        }
      } else {
        try {
          const listRes = await fetch(
            `${API_BASE}/reviews/${encodeURIComponent(book.isbn)}`,
            { cache: "no-store" }
          );
          if (listRes.ok) {
            const list = await listRes.json();
            setReviews(Array.isArray(list) ? list : []);
          }
        } catch (refetchErr) {
          console.error("Error while refetching reviews list", refetchErr);
        }
      }

      setIsEditing(false);
      setCurrentReviewPage(1);
    } catch (e) {
      console.error("Unexpected error in handleSave", e);
      alert("Unexpected error while saving: " + (e?.message || e));
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
                    value={userRating ?? 0} 
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
                Reviews: {reviews.length}
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
                          {r.username || `User #${r.user_id}`}
                        </span>
                        <span className="text-[0.7rem] text-slate-400">
                          {new Date(r.time).toISOString().slice(0, 10)}
                        </span>
                      </div>

                      {/* Rating on the right, like 9/10 */}
                      {r.rating != null && (
                        <span className="text-sm font-semibold text-[#023147]">
                          {r.rating}/10
                        </span>
                      )}
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
