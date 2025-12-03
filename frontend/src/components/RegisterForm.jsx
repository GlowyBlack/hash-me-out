"use client";
import { useState } from "react";

export default function RegisterForm({ setFormType, onSuccess }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Registration failed");

      if (onSuccess) onSuccess(); 

    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="relative w-full max-w-sm">
      {/* Close Button */}
      <button
        className="absolute top-0 right-0 mt-2 mr-2 bg-gray-100 hover:bg-gray-300 text-gray-800 font-semibold py-1 px-3 rounded-lg shadow-md hover:scale-105"
        onClick={() => setFormType(null)}
        type="button"
      >
        X
      </button>

      <form
        onSubmit={handleRegister}
        className="flex flex-col gap-4 bg-white p-6 rounded-xl shadow-md mt-8"
      >
        <h1 className="font-serif text-3xl font-extrabold text-neutral-900 text-center">
          Register Below
        </h1>

        {error && <p className="text-red-500 text-center">{error}</p>}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400"
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400"
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-400"
          required
        />

        <button
          type="submit"
          className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 px-6 rounded-lg shadow-md hover:scale-105"
        >
          Register
        </button>
      </form>
    </div>
  );
}
