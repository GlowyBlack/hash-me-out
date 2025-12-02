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
              <div
                className="text-xl  text-gray-900 cursor-pointer"
                onClick={goToProfile}
              >
                Profile
              </div>

              <button
                onClick={handleLogout}
                className="bg-yellow-400 hover:bg-yellow-500 text-gray-600 font-semibold py-2 px-4 rounded-lg shadow-md hover:scale-105"
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
