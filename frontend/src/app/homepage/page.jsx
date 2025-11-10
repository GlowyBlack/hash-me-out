"use client";

import { useState } from "react";
import LoginForm from "../../components/forms/loginForm";
import RegisterForm from "../../components/forms/registerForm";

export default function GuestHomePage() {
  const [search, setSearch] = useState("");
  const [formType, setFormType] = useState(null);

  const handleSearch = (e) => {
    e.preventDefault();
    console.log("Searching for:", search);
    // TODO: implement search logic
  };

  return (
    
    <div className="min-h-screen w-screen bg-gray-50 overflow-x-hidden">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          {/* Left: Logo / Home */}
          <div className="text-xl font-bold cursor-pointer">
            Home
          </div>
          {/* Right: Login & Register */}
          <div className= " space-x-4 flex justify-between items-center">
            <button className="bg-white border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-100"
            onClick={() => setFormType("login")}
            >  
            Login
            </button>
            <button className="bg-amber-200 hover:bg-yellow-400 px-4 py-2 rounded-lg font-semibold"
            onClick={() => setFormType("register")}
            >
            Register
            </button>
          </div>
         </div>
      </header>

      {/* Show Forms Conditionally */}
      <div className="w-full max-w-md">
        {formType === "login" && <LoginForm setFormType={setFormType} />}
        {formType === "register" && <RegisterForm setFormType={setFormType} />}
      </div>

      {/* Main content */}
      {formType === null && (
         <>
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

      {/* Search bar under header */}
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
    </>
    )}
    </div>
  );
}
