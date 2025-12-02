"use client";
import { useRouter } from "next/navigation";

export default function Header({
  user,
  setFormType,
  handleLogout,
  goToProfile,
  compact = false,
  showProfileButton = true,
}) {
  const router = useRouter();

  const goHome = () => {
    router.push("/homepage"); // or "/" if that's your main route
  };

  const isLoggedIn = !!user;

  return (
    <header className="w-full bg-white border-b border-[#E4ECFF]">
      <div
        className={`max-w-6xl mx-auto px-6 ${
          compact ? "py-2" : "py-3"
        } flex items-center justify-between`}
      >
        {/* Left: Home link */}
        <button
          type="button"
          onClick={goHome}
          className="text-base font-semibold text-gray-700 cursor-pointer"
        >
          Home
        </button>

        {/* Right: auth / profile actions */}
        <div className="flex items-center gap-4">
          {!isLoggedIn ? (
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
