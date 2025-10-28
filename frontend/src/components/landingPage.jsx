"use client";
import { useState } from "react";
import LoginForm from "./loginForm";
import RegisterForm from "./registerForm";
import HomeForm from "./homeForm";

export default function LandingPage() {
  const [formType, setFormType] = useState(null);

  return (
    <main className="min-h-screen bg-amber-100 flex flex-col items-center justify-center text-center px-6">
      {/* Show welcome message only if no form is active */}
      {formType === null && (
        <>
          <h1 className="font-serif text-5xl font-extrabold text-neutral-800 mb-6">
            Welcome to BookReview.com
          </h1>
          <p className="text-lg text-neutral-800 mb-10 max-w-lg">
            Discover and share your thoughts on your favorite books. <br /> 
            Join our community or continue as a guest to explore reviews.
          </p>
        </>
      )}

      {/* Buttons Section */}
      {formType === null && (
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <button
            className="bg-amber-300 hover:bg-amber-400 text-black font-semibold py-3 px-8 rounded-xl shadow-md transition-transform transform hover:scale-105"
            onClick={() => setFormType("login")}
          >
            Login
          </button>
          <button
            className="bg-amber-300 hover:bg-amber-400 text-black font-semibold py-3 px-8 rounded-xl shadow-md transition-transform transform hover:scale-105"
            onClick={() => setFormType("register")}
          >
            Register
          </button>
        </div>
      )}

      {/* Show Forms Conditionally */}
      <div className="w-full max-w-md">
        {formType === "login" && <LoginForm setFormType={setFormType} />}
        {formType === "register" && <RegisterForm setFormType={setFormType} />}
        {formType === "home" && <HomeForm />}
      </div>

      {/* Guest Option */}
      {formType === null && (
        <button
          className="mt-4 font-medium text-yellow-700 hover:text-yellow-800 underline bg-transparent transition-transform transform hover:scale-105"
          onClick={() => setFormType("home")}
        >
          Proceed as Guest
        </button>
      )}
    </main>
  );
}
