"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

import Header from "../../components/Header";
import AuthPopup from "../../components/AuthPopup/AuthPopup";
import SearchBar from "../../components/SearchBar/SearchBar";
import SearchList from "../../components/SearchResults/SearchList";
import Pagination from "../../components/SearchResults/Pagination";

export default function HomePage() {
  const router = useRouter();

  // ============================
  // USER / AUTH STATE
  // ============================
  const [user, setUser] = useState(null);
  const [formType, setFormType] = useState(null);

  // ============================
  // SEARCH STATE
  // ============================
  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ============================
  // PAGINATION
  // ============================
  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 5;

  const indexOfLast = currentPage * resultsPerPage;
  const indexOfFirst = indexOfLast - resultsPerPage;
  const currentResults = results.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(results.length / resultsPerPage);

  // ============================
  // LIVE SEARCH STATE
  // ============================
  const [liveResults, setLiveResults] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  // ============================
  // ELLIPSIS PAGE JUMP STATE
  // ============================
  const [ellipsisOpen, setEllipsisOpen] = useState(null);
  const [jumpPage, setJumpPage] = useState("");

  // ============================
  // REF for click-outside closing
  // ============================
  const searchRef = useRef(null);

  // ----------------------------
  // Decode token & load user
  // ----------------------------
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      const decoded = JSON.parse(atob(token.split(".")[1]));
      setUser(decoded);
    }
  }, []);

  // ----------------------------
  // Close live search on click outside
  // ----------------------------
  useEffect(() => {
    function handleClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setLiveResults([]);
        setIsTyping(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // ----------------------------
  // Full search handler (non-live)
  // ----------------------------
  const handleSearch = async (e) => {
    e.preventDefault();
    setLiveResults([]);  // hide dropdown
    setIsTyping(false);

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const res = await fetch(`http://localhost:8000/books/search?query=${search}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setResults(data);
      setCurrentPage(1);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  // ----------------------------
  // LIVE SEARCH: debounced
  // ----------------------------
  useEffect(() => {
    if (!search.trim()) {
      setLiveResults([]);
      return;
    }

    setIsTyping(true);

    const timeout = setTimeout(async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/books/live-search?query=${search}`
        );
        const data = await res.json();
        setLiveResults(data);
      } catch (err) {
        console.log(err);
      }
      setIsTyping(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, [search]);

  // ----------------------------
  // Logout handler
  // ----------------------------
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/");
  };

  // ----------------------------
  // Profile route
  // ----------------------------
  const goToProfile = () => {
    router.push("/profile");
  };

  // ----------------------------
  // When login/register succeeds
  // ----------------------------
  const handleLoginSuccess = () => {
    setFormType(null);

    const token = localStorage.getItem("access_token");
    if (token) {
      const decoded = JSON.parse(atob(token.split(".")[1]));
      setUser(decoded);
    }
  };

  // =============================
  // RETURN UI (now much cleaner)
  // =============================
  return (
    <div className="relative min-h-screen bg-gray-50">

      {/* HEADER */}
      <Header
        user={user}
        setFormType={setFormType}
        handleLogout={handleLogout}
        goToProfile={goToProfile}
      />

      {/* AUTH POPUP */}
      <AuthPopup
        formType={formType}
        setFormType={setFormType}
        handleLoginSuccess={handleLoginSuccess}
      />

      {/* WELCOME TEXT */}
      <main className="max-w-7xl mx-auto px-6 py-12 text-center">
        <h1 className="text-4xl font-bold mb-6 text-gray-900">
          {user ? `Welcome back, ${user.username}!` : "Welcome to Our Library!"}
        </h1>
        <p className="text-lg text-gray-700">
          Browse books, search by title or author, and register to make requests.
        </p>
      </main>

      {/* SEARCH BAR + LIVE SEARCH */}
      <SearchBar
        search={search}
        setSearch={setSearch}
        handleSearch={handleSearch}
        liveResults={liveResults}
        isTyping={isTyping}
        searchRef={searchRef}
      />

      {/* RESULTS LIST */}
      <div className="max-w-7xl mx-auto px-6 mt-6">
        <SearchList results={currentResults} />
      </div>

      {/* PAGINATION */}
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        setCurrentPage={setCurrentPage}
        ellipsisOpen={ellipsisOpen}
        setEllipsisOpen={setEllipsisOpen}
        jumpPage={jumpPage}
        setJumpPage={setJumpPage}
      />

    </div>
  );
}
