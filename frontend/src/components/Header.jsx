"use client";
import { useRouter } from "next/navigation";

export default function Header({ user, setFormType, handleLogout, goToProfile }) {
  const router = useRouter();

  return (
    <header className="bg-white shadow-md w-full fixed top-0 left-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        
        {/* LEFT SIDE: Home + Dashboard */}
        <div className="flex items-center space-x-6">
          <div
            className="text-xl font-bold text-gray-900 cursor-pointer"
            onClick={() => router.push("/homepage")}
          >
            Home
          </div>

          {user?.is_admin && (
            <div
              className="text-xl font-bold text-gray-900 cursor-pointer"
              onClick={() => router.push("/admin")}
            >
              Dashboard
            </div>
          )}
        </div>

        {/* RIGHT SIDE: Buttons */}
        <div className="flex items-center space-x-4">
          {!user ? (
            <>
              <button
                className="rounded-full border border-slate-300 bg-white text-slate-800 text-sm font-semibold px-6 py-3 hover:bg-slate-50 transition"
                onClick={() => setFormType("login")}
              >
                Login
              </button>

              <button
                className="rounded-full border border-[#ffb803] bg-[#ffb803] text-slate-900 text-sm font-semibold px-4 py-3 shadow-sm hover:bg-[#f5a800] hover:border-[#f5a800] transition"
                onClick={() => setFormType("register")}
              >
                Register
              </button>
            </>
          ) : (
            <>
              <div
                onClick={goToProfile}
                className="cursor-pointer rounded-full border border-slate-300 bg-white text-slate-800 text-sm font-semibold px-6 py-3 hover:bg-slate-50 transition"
              >
                Profile
              </div>

              <button
                onClick={handleLogout}
                className="rounded-full border border-[#ffb803] bg-[#ffb803] text-slate-900 text-sm font-semibold px-4 py-3 shadow-sm hover:bg-[#f5a800] hover:border-[#f5a800] transition"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
