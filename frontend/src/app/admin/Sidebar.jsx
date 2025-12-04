"use client";

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: "users", label: "Users" },
    { id: "requests", label: "Requests" },
    { id: "suspensions", label: "Suspensions" },
    { id: "books", label: "Books" },
  ];

  return (
    <div className="w-64 bg-white border-r shadow-md p-6">
      <h2 className="text-gray-800 text-2xl font-bold mb-6">Actions</h2>

      <ul className="space-y-3">
        {menuItems.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => setActiveTab(item.id)}
              className={`w-full text-left px-4 py-2 rounded-lg font-medium ${
                activeTab === item.id
                  ? "bg-yellow-400 text-gray-800"
                  : "text-gray-700 hover:bg-gray-200"
              }`}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
