"use client";
import { useState } from "react";

export default function LoginForm() {
  const [input, setInput] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    let email = "";
    let username = "";

    if (emailRegex.test(input)) {
      email = input;
    } else {
      username = input;
    }
    
    console.log("Logging in with:", { email, password });

    // TODO: replace with actual login logic****************************



  };



  return (
    <form
      onSubmit={handleLogin}
      className="flex flex-col gap-4 w-full max-w-sm bg-white p-6 rounded-xl shadow-md"
    >
      <input
        type="text"
        placeholder="Username or Email"
        value={input}
        onChange={(e) => setInput(e.target.value)}
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
        className="bg-yellow-400 hover:bg-yellow-500 text-black-200 font-semibold py-3 px-6 rounded-lg shadow-md transition-all transform hover:scale-105"
      >
        Login
      </button>
    </form>
  );
}
