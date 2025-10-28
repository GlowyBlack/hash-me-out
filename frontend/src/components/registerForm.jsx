"use client";
import { useState } from "react";

export default function RegisterForm() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    // TODO: replace with actual login logic****************************
    // keep track of whos currently signed in in the local storage 
    console.log("Logging in with:", { email, password });
  };

  return (
    <form
      onSubmit={handleLogin}
      className="flex flex-col gap-4 w-full max-w-sm bg-white p-6 rounded-xl shadow-md"
    >
      <input
        type="username"
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
        className="bg-yellow-400 hover:bg-yellow-500 text-black-200  font-semibold py-3 px-6 rounded-lg shadow-md transition-all transform hover:scale-105"
      >
        Register
      </button>
    </form>
  );
}
