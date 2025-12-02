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
                className="bg-white border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100"
                onClick={() => setFormType && setFormType("login")}
              >
                Login
              </button>

              <button
                className="bg-yellow-400 hover:bg-yellow-500 text-gray-600 px-4 py-2 rounded-lg font-semibold"
                onClick={() => setFormType && setFormType("register")}
              >
                Register
              </button>
            </>
          ) : (
            <>
              {/* Profile button is optional now */}
              {showProfileButton && goToProfile && (
                <button
                  onClick={goToProfile}
                  className="bg-white border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100"
                >
                  Profile
                </button>
              )}

              <button
                onClick={handleLogout}
                className="bg-yellow-400 hover:bg-yellow-500 text-gray-600 font-semibold py-3 px-6 rounded-lg shadow-md hover:scale-105"
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
