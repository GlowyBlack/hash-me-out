// src/app/books/[isbn]/page.jsx

import BookDetailPage from "@/components/bookDetails";

export default async function BookPage({ params }) {
  const { isbn } = params;

  // Adjust this to your backend base URL
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  // Fetch book, average rating and reviews in parallel
  const [bookRes, avgRes, reviewsRes] = await Promise.all([
    fetch(`${API_BASE}/books/${isbn}`, { cache: "no-store" }),
    fetch(`${API_BASE}/ratings/books/${isbn}/average`, { cache: "no-store" }),
    fetch(`${API_BASE}/reviews/${isbn}`, { cache: "no-store" }),
  ]);

  if (!bookRes.ok) {
    // Very simple error handling
    // You can replace with a proper 404 page
    throw new Error("Book not found");
  }

  const book = await bookRes.json();
  const avgRating = avgRes.ok
    ? await avgRes.json()
    : { isbn, avg_rating: 0, count: 0 };
  const reviews = reviewsRes.ok ? await reviewsRes.json() : [];

  return (
    <BookDetailPage
      book={book}
      avgRating={avgRating}
      initialReviews={reviews}
    />
  );
}
