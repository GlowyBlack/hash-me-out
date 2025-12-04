"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

import Header from "@/components/Header";
import AuthPopup from "@/components/AuthPopup/AuthPopup";
import BookDetailPage from "@/components/BookDetails";

export default function BookPageClient({ book, avgRating, reviews, similarBooks }) {
  const router = useRouter();

  // Auth
  const [user, setUser] = useState(null);
  const [formType, setFormType] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      try {
        const decoded = JSON.parse(atob(token.split(".")[1]));
        setUser(decoded);
      } catch {}
    }
  }, []);

  const handleLoginSuccess = () => {
    const token = localStorage.getItem("access_token");
    if (token) {
      const decoded = JSON.parse(atob(token.split(".")[1]));
      setUser(decoded);
    }
    setFormType(null);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/");
  };

  return (
    <div className="relative min-h-screen bg-gray-50">

      {/* Header */}
      <Header
        user={user}
        setFormType={setFormType}
        handleLogout={handleLogout}
        goToProfile={() => router.push("/profile")}
      />

      {/* Auth Popup */}
      <AuthPopup
        formType={formType}
        setFormType={setFormType}
        handleLoginSuccess={handleLoginSuccess}
      />

      {/* Main Book Details */}
      <div className="py-28">
        <BookDetailPage
          book={book}
          avgRating={avgRating}
          initialReviews={reviews}
          user={user}
          similarBooks={similarBooks}
          onRequireAuth={() => setFormType("login")}
        />
      </div>
    </div>
  );
}
