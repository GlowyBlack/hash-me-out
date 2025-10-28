"use client";
import { useState } from "react";
import LoginForm from "@/components/loginForm";
import RegisterForm from "@/components/registerForm";

export default function Home() {
  const [formType, setFormType] = useState(null);

  return (
    <main className="min-h-screen bg-amber-100 flex flex-col items-center justify-center text-center px-6">
      <h1 className="font-serif text-5xl font-extrabold text-neutral-40 mb-6">
        Welcome to BookReview.com
      </h1>
      <p className="text-lg text-neutral-40 mb-10 max-w-lg">
        Discover and share your thoughts on your favorite books. <br /> 
        Join our community or continue as a guest to explore reviews.
      </p>

      {/* Buttons Section */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <button
          className="bg-amber-300 hover:bg-amber-400 text-black-200 font-semibold py-3 px-8 rounded-xl shadow-md transition-colors transition-transform transform hover:scale-105"
          onClick={() => setFormType("login")}
        >
          Login
        </button>
        <button
          className="bg-amber-300 hover:bg-amber-400 text-black-200 font-semibold py-3 px-8 rounded-xl shadow-md transition-colors transition-transform transform hover:scale-105"
          onClick={() => setFormType("register")}
        >
          Register
        </button>
      </div>

    {/* Show Forms Conditionally */}
    {formType === "login" && <LoginForm />}
    {formType === "register" && <RegisterForm />}


      {/* Guest Option */}
      <button
        className="mt-4 font-medium text-yellow-700 hover:text-yellow-800 underline bg-transparent transition-transform transform hover:scale-105"
      >
        Proceed as Guest 
      </button>
    </main>
  );
}
