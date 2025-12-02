"use client";

export default function Header({ user, setFormType, handleLogout, goToProfile }) {
  return (
    <header className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div className="text-xl font-bold text-gray-900 cursor-pointer">Home</div>

        <div className="space-x-4 flex justify-end items-center">
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
              <button
                onClick={goToProfile}
                className="rounded-full border border-slate-300 bg-white text-slate-800 text-sm font-semibold px-6 py-3 hover:bg-slate-50 transition"
              >
                Profile
              </button>

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
