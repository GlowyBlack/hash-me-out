import BookPageClient from "@/components/Books/BookPageClient";

export default async function BookPage({ params }) {
  const { isbn } = params;

  const API_BASE =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  const [bookRes, ratingRes, reviewsRes, simRes] = await Promise.all([
    fetch(`${API_BASE}/books/${isbn}`, { cache: "no-store" }),
    fetch(`${API_BASE}/ratings/books/${isbn}/average`, { cache: "no-store" }),
    fetch(`${API_BASE}/reviews/${isbn}`, { cache: "no-store" }),
    fetch(`${API_BASE}/recommendation/${isbn}`, { cache: "no-store" }),
  ]);

  if (!bookRes.ok) {
    return <div className="p-10 text-center text-gray-600">Book not found.</div>;
  }

  const book = await bookRes.json();
  const avgRating = ratingRes.ok ? await ratingRes.json() : { avg_rating: 0, count: 0 };
  const reviews = reviewsRes.ok ? await reviewsRes.json() : [];
  const similarBooks = simRes.ok ? await simRes.json() : [];

  return (
    <BookPageClient
      book={book}
      avgRating={avgRating}
      reviews={reviews}
      similarBooks={similarBooks}
    />
  );
}
