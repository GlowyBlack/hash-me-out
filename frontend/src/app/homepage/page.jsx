"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import RecommendedForYou from "@/components/Recommended/RecommendedForYou";
import FilterModal from "@/components/SearchBar/FilterModal"
import Header from "@/components/Header";
import AuthPopup from "@/components/AuthPopup/AuthPopup";
import SearchBar from "@/components/SearchBar/SearchBar";
import SearchList from "@/components/SearchResults/SearchList";
import Pagination from "@/components/SearchResults/Pagination";



export default function HomePage() {
  const router = useRouter();

  const [user, setUser] = useState(null);
  const [formType, setFormType] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [suspensionInfo, setSuspensionInfo] = useState(null);
  const [recommended, setRecommended] = useState([]);

  const [search, setSearch] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);


  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [filters, setFilters] = useState({
    author: null,
    genre: null,
    year_min: null,
    year_max: null,
  });

  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 5;

  const indexOfLast = currentPage * resultsPerPage;
  const indexOfFirst = indexOfLast - resultsPerPage;
  const currentResults = results.slice(indexOfFirst, indexOfLast);
  const totalPages = Math.ceil(results.length / resultsPerPage);

  const [liveResults, setLiveResults] = useState([]);
  const [liveLoading, setLiveLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const [ellipsisOpen, setEllipsisOpen] = useState(null);
  const [jumpPage, setJumpPage] = useState("");

  const searchRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setAuthChecked(true);
      return;
    }

    async function fetchMe() {
      try {
        const res = await fetch("http://localhost:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) {
          localStorage.removeItem("access_token");
          setUser(null);
          setSuspensionInfo(null);
        } else {
          const data = await res.json();
          setUser(data);

          if (data.is_suspended) {
            setSuspensionInfo({
              suspended_until: data.suspended_until,
              reason: data.suspension_reason,
            });
          } else {
            setSuspensionInfo(null);
          }
        }
      } catch (err) {
        console.error("Failed to load user:", err);
      } finally {
        setAuthChecked(true);
      }
    }

    fetchMe();
  }, []);

  useEffect(() => {
  async function loadRecommended() {
    if (!user) return;

    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`http://localhost:8000/personalized`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        const data = await res.json();
        setRecommended(data);
      }
    } catch (err) {
      console.error("Failed to load personalized recs:", err);
    }
  }

  loadRecommended();
}, [user]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setLiveResults([]);
        setIsTyping(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () =>
      document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLiveResults([]);
    setIsTyping(false);
    setHasSearched(true);

    setLoading(true);
    setError("");
    setResults([]);
    setHasSearched(false); // reset before the request

    const params = new URLSearchParams({
      query: search,
      ...(filters.author && { author: filters.author }),
      ...(filters.genre && { genre: filters.genre }),
      ...(filters.year_min && { year_min: filters.year_min }),
      ...(filters.year_max && { year_max: filters.year_max }),
    });

    try {
      const res = await fetch(`http://localhost:8000/books/search?${params}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setResults(data);
      setCurrentPage(1);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
    setHasSearched(true); // search is now done
  };

  useEffect(() => {
    if (!search.trim()) {
      setLiveResults([]);
      return;
    }

    setLiveLoading(true)
    setIsTyping(true);

    const timeout = setTimeout(async () => {
      try {
        const params = new URLSearchParams({
          query: search,
          ...(filters.author && { author: filters.author }),
          ...(filters.genre && { genre: filters.genre }),
          ...(filters.year_min && { year_min: filters.year_min }),
          ...(filters.year_max && { year_max: filters.year_max }),
          limit: 10,
        }); 
        const res = await fetch(
          `http://localhost:8000/books/live-search?${params}`
        );
        const data = await res.json();
        setLiveResults(data);
      } catch (err) {
        console.log(err);
      }
      setLiveLoading(false);
      setIsTyping(false);
    }, 300);

    return () => clearTimeout(timeout);
  }, [search]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    setSuspensionInfo(null);
    router.push("/");
  };

  const goToProfile = () => {
    router.push("/profile");
  };

  const handleLoginSuccess = async () => {
    setFormType(null);

    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
      const res = await fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const data = await res.json();
        setUser(data);
        if (data.is_suspended) {
          setSuspensionInfo({
            suspended_until: data.suspended_until,
            reason: data.suspension_reason,
          });
        } else {
          setSuspensionInfo(null);
        }
      }
    } catch (err) {
      console.error("Failed to fetch current user after login:", err);
    }
  };

  const untilText =
    suspensionInfo && suspensionInfo.suspended_until
      ? new Date(suspensionInfo.suspended_until).toLocaleString()
      : "further notice";

  if (!authChecked) {
    return <div className="min-h-screen bg-gray-50" />;
  }

  if (suspensionInfo) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header
          user={user}
          setFormType={setFormType}
          handleLogout={handleLogout}
          goToProfile={goToProfile}
        />

        <div className="flex-1 flex items-center justify-center px-4">
          <div className="max-w-xl w-full bg-white shadow-md rounded-lg p-8 text-center">
            <h1 className="text-3xl font-bold mb-4 text-red-600">
              Your account is suspended
            </h1>
            <p className="mb-2">
              You are suspended until{" "}
              <span className="font-semibold">{untilText}</span>.
            </p>
            {suspensionInfo.reason && (
              <p className="text-gray-700">
                <span className="font-semibold">Reason:</span>{" "}
                {suspensionInfo.reason}
              </p>
            )}
            <p className="mt-4 text-sm text-gray-500">
              If you believe this is a mistake, please contact an
              administrator.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen  bg-gray-50">
      <Header
        user={user}
        setFormType={setFormType}
        handleLogout={handleLogout}
        goToProfile={goToProfile}
      />

      <AuthPopup
        formType={formType}
        setFormType={setFormType}
        handleLoginSuccess={handleLoginSuccess}
      />

      <main className="max-w-7xl mx-auto px-6 py-28 text-center">
        <h1 className="text-4xl font-bold mb-6 text-gray-900">
          {user
            ? `Welcome back, ${user.username}!`
            : "Welcome to Our Library!"}
        </h1>
        <p className="text-lg text-gray-700">
          Browse books, search by title or author, and register to make
          requests.
        </p>
      </main>

      <SearchBar
        search={search}
        setSearch={setSearch}
        handleSearch={handleSearch}
        liveResults={liveResults}
        liveLoading={liveLoading}
        isTyping={isTyping}
        searchRef={searchRef}
        setLiveResults={setLiveResults}   
        onOpenFilters={() => setIsFilterOpen(true)}
      />


      <FilterModal
        isOpen={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        initialFilters={filters}
        onApply={(newFilters) => setFilters(newFilters)}
      />

      {user && recommended.length > 0 && (
        <RecommendedForYou books={recommended} />
      )}

      <div className="max-w-7xl mx-auto px-6 mt-6 min-h-8">
        {loading && <p>Loading...</p>}
        {error && <p className="text-red-500">{error}</p>}

        {/* Only show results AFTER the user clicked Search */}
        {!loading && !error && hasSearched && (
          <SearchList
            results={currentResults}
            hasSearched={hasSearched}
            query={search}
          />
        )}
      </div>
      
      <div className="pb-20">
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
    </div>
  );
}
