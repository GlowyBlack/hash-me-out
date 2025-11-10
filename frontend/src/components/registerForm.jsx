"use client";
import { useState } from "react";

export default function RegisterForm({ setFormType }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = (e) => {
    e.preventDefault();
    console.log("Registering with:", { username, email, password });
  };

  return (
    <div className="relative w-full max-w-sm">
      {/* Back button at top right */}
      <button
        className="absolute top-0 right-0 mt-2 mr-2 bg-gray-100 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-lg shadow-md transition-transform transform hover:scale-105"
        onClick={() => setFormType(null)} // now works
        type="button"
      >
        X
      </button>

      <form
        onSubmit={handleRegister}
        className="flex flex-col gap-4 bg-white p-6 rounded-xl shadow-md mt-8"
      >
        <h1 className="font-serif text-3xl font-extrabold text-neutral-800 mb-1 text-center">
          Register Below
        </h1>
        <p className="text-sm text-neutral-700 mb-4 text-center">
          Enter your username, email, and password to continue.
        </p>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
          required
        />
        <button
          type="submit"
          className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 px-6 rounded-lg shadow-md transition-all transform hover:scale-105"
        >
          Register
        </button>
      </form>
    </div>
  );
}
