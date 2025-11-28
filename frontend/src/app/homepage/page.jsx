"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const [search, setSearch] = useState("");
  const [user, setUser] = useState(null); // store user info
  const router = useRouter();

  useEffect(() => {
    // Check localStorage for token
    const token = localStorage.getItem("access_token");
    if (token) {
      // Optionally decode token for username or user_id
      const decoded = JSON.parse(atob(token.split(".")[1]));
      setUser(decoded); // store decoded info
    }
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    console.log("Searching for:", search);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/"); // redirect to homepage or login
  };

  const goToProfile = () => {
    router.push("/profile"); // make sure you have a profile page
  };

  return (
    <div className="min-h-screen min-w-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          {/* Left: Logo / Home */}
          <div className="text-xl font-bold cursor-pointer">Home</div>

          {/* Right: conditional buttons */}
          <div className="space-x-4 flex justify-between items-center">
            {!user ? (
              <>
                <button className="bg-white border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-100">
                  Login
                </button>
                <button className="bg-amber-200 hover:bg-yellow-400 px-4 py-2 rounded-lg font-semibold">
                  Register
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={goToProfile}
                  className="bg-white border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-100"
                >
                  Profile
                </button>
                <button
                  onClick={handleLogout}
                  className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 px-6 rounded-lg shadow-md transition-all transform hover:scale-105"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-12 flex justify-center">
        <div className="flex-col justify-center">
          <div className="flex justify-center">
            <h1 className="text-4xl font-bold mb-6">Welcome to Our Library!</h1>
          </div>
          <p className="text-lg text-gray-700">
            Browse books, search by title or author, and register to make requests.
          </p>
        </div>
      </main>

      {/* Search bar */}
      <div className="bg-gray-50 py-6">
        <div className="max-w-7xl mx-auto px-6">
          <form onSubmit={handleSearch} className="flex max-w-md mx-auto">
            <input
              type="text"
              placeholder="Search..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
            <button
              type="submit"
              className="bg-amber-200 hover:bg-yellow-500 px-4 py-2 rounded-r-lg font-semibold"
            >
              Search
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
