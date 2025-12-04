"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Pagination from "./SearchResults/Pagination";
import AddToReadingListButton from "./readinglist/AddToReadingListButton";
import SimilarBooksSidebar from "./Recommended/SimilarBooks";


export default function BookDetailPage({
  book,
  avgRating,
  initialReviews,
  similarBooks,
  user,
  onRequireAuth
}) {

  const router = useRouter();

  // ===============================
  // DISPLAY FIELDS
  // ===============================
  const displayTitle = book.book_title;
  const displayYear = book.year_of_publication;
  const displayPublisher = book.publisher;
  const displayAuthor = book.author;
  const coverUrl = book.image_url_l || book.image_url_m || book.image_url_s;

  const initialAvgRating = avgRating?.avg_rating ?? 0;
  const initialRatingCount = avgRating?.count ?? 0; 

  // ===============================
  // INTERNAL STATE
  // ===============================
  const [reviews, setReviews] = useState(initialReviews || []);
  const [userRating, setUserRating] = useState(null);
  const [userComment, setUserComment] = useState("");
  const [isEditing, setIsEditing] = useState(true);
  const [saving, setSaving] = useState(false);
  const [myReviewId, setMyReviewId] = useState(null);

  // ===============================
  // PAGINATION
  // ===============================
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

  // ===============================
  // Load user's existing review
  // ===============================
  useEffect(() => {
    if (!user || reviews.length === 0) return;

    const mine = reviews.find((r) => r.user_id === user.id);
    if (mine) {
      setMyReviewId(mine.review_id);
      setUserComment(mine.comment);
      setIsEditing(false);
    }
  }, [user, reviews]);

  // ===============================
  // SAVE REVIEW + RATING
  // ===============================
  async function handleSave() {
    if (!user) {
      onRequireAuth();
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      onRequireAuth();
      return;
    }

    if (!userComment || userComment.trim().length < 8) {
      alert("Please write at least 8 characters for your review.");
      return;
    }

    try {
      setSaving(true);

      // ---- 1) SAVE RATING ----
      if (userRating !== null) {
        await fetch(`${API_BASE}/ratings/books/${book.isbn}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ rating: userRating }),
        });
      }

      // ---- 2) SAVE REVIEW ----
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

      // ---- 3) Update UI ----
      let savedReview = null;
      try {
        savedReview = await reviewRes.json();
      } catch {
        // if no JSON body (e.g., 204), refetch
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
        // fallback refetch
        const listRes = await fetch(`${API_BASE}/reviews/${book.isbn}`);
        if (listRes.ok) {
          const list = await listRes.json();
          setReviews(Array.isArray(list) ? list : []);
        }
      }

      setIsEditing(false);
      setCurrentReviewPage(1);

    } catch (e) {
      console.error("Save error:", e);
      alert("Error saving your review");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="px-6 md:px-4 py-10 max-w-7xl mx-auto">
      <div className="flex flex-col lg:flex-row gap-10">

        {/* LEFT: Book Info */}
        <div className="w-full lg:max-w-xs bg-white border rounded-3xl shadow-md p-6 self-start">
          <div className="relative flex justify-center mb-4">
            {coverUrl ? (
              <img
                src={coverUrl}
                alt={displayTitle}
                className="w-48 h-auto rounded-xl shadow-md object-cover"
              />
            ) : (
              <div className="w-48 h-64 bg-gray-100 rounded-xl flex items-center justify-center text-gray-500">
                No cover
              </div>
            )}

            <div className="absolute top-2 right-2">
              <AddToReadingListButton
                book={book}
                user={user}
                onRequireAuth={onRequireAuth}
              />
            </div>
          </div>
          <div className="text-gray-900">
            <h1 className=" text-2xl font-semibold mb-1">{displayTitle}</h1>
            <p className="text-gray-900 mb-3">by {displayAuthor}</p>
            <p className="text-gray-600"><strong>Year:</strong> {displayYear || "N/A"}</p>
            <p className="text-gray-600"><strong>Publisher:</strong> {displayPublisher || "N/A"}</p>
            <p className="text-gray-600"><strong>ISBN:</strong> {book.isbn}</p>
          </div>
        </div>

        {/* Middle: Reviews + Rating */}
        <div className="flex-1 flex flex-col gap-6">

          {/* Rating */}
          <div className="text-gray-900 bg-white border rounded-2xl shadow p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold">Your Rating</h2>
              <span className="bg-amber-100 px-3 py-1 rounded-full text-xs">
                Avg: {initialAvgRating.toFixed(1)} / 10
              </span>
            </div>

            <div className="flex items-center gap-4 ">
              <span>0</span>
              <input
                type="range"
                min="0"
                max="10"
                value={userRating ?? 0}
                onChange={(e) => setUserRating(Number(e.target.value))}
                className="flex-1 accent-yellow-500"
              />
              <span>10</span>
              <span className="w-16 text-right font-semibold">
                {userRating ?? "—"}
              </span>
            </div>
          </div>

          {/* Review Editor */}
          <div className="bg-white border rounded-2xl shadow p-5 text-gray-900">
            <div className="flex justify-between mb-2">
              <h2 className="font-semibold">Your Review</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-xs border px-3 py-1 rounded-full"
                >
                  Edit
                </button>
              )}
            </div>

            <textarea
              className="w-full min-h-[120px] border rounded-xl p-2"
              value={userComment}
              disabled={!isEditing}
              onChange={(e) => setUserComment(e.target.value)}
              maxLength={750}
            />

            <div className="flex justify-between mt-2 text-xs">
              <span>{userComment.length}/750</span>
              <button
                onClick={handleSave}
                disabled={!isEditing || saving}
                className="bg-yellow-400 hover:bg-yellow-500 px-4 py-1 text-sm font-semibold rounded-full"
              >
                {saving ? "Saving..." : "Save Review"}
              </button>
            </div>
          </div>

          {/* Reviews */}
          <div>
            <h2 className="font-semibold mb-2 text-gray-900">
              Reviews ({reviews.length})
            </h2>

            {reviews.length === 0 && (
              <p className="text-gray-500 text-sm">No reviews yet.</p>
            )}

            <div className="space-y-3">
              {currentReviews.map((r) => (
                <div key={r.review_id} className="bg-white border rounded-xl p-4">
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-900 font-semibold">{r.username}</span>
                    {r.rating !== null && (
                      <span className="text-yellow-600">{r.rating}/10</span>
                    )}
                  </div>
                  <p className=" text-gray-500 text-sm whitespace-pre-line">{r.comment}</p>
                </div>
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
          </div>
        </div>
        {/* Right: Similar Books */}
        <SimilarBooksSidebar similarBooks={similarBooks} />


      </div>
    </div>
  );
}
