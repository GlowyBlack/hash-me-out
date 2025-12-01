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
                className="bg-white border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100"
                onClick={() => setFormType("login")}
              >
                Login
              </button>

              <button
                className="bg-yellow-400 hover:bg-yellow-500 text-gray-600 px-4 py-2 rounded-lg font-semibold"
                onClick={() => setFormType("register")}
              >
                Register
              </button>
            </>
          ) : (
            <>
              <button
                onClick={goToProfile}
                className="bg-white border border-gray-300 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-100"
              >
                Profile
              </button>

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
