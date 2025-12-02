"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Header from "../../components/Header";
import Sidebar from "./Sidebar";
import Users from "./Users";
import Requests from "./Requests";
import Suspensions from "./Suspensions";
import Books from "./Books";

export default function AdminPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState("users");
  const [loadingUser, setLoadingUser] = useState(true);

  // Load user from localStorage
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      try {
        const decoded = JSON.parse(atob(token.split(".")[1]));
        setUser(decoded);
      } catch (err) {
        console.error("Failed to decode token", err);
        setUser(null);
      }
    } else {
      setUser(null);
    }
    setLoadingUser(false);
  }, []);

  // Redirect non-admins to homepage
  useEffect(() => {
    if (!loadingUser && (!user || !user.is_admin)) {
      router.replace("/homepage");
    }
  }, [user, loadingUser, router]);

  // Handlers
  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.push("/");
  };

  const goToProfile = () => {
    router.push("/profile");
  };

  if (loadingUser || !user?.is_admin) return null; // wait until user loaded

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col pt-20">
      <Header user={user} handleLogout={handleLogout} goToProfile={goToProfile} />

      <div className="flex flex-1">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <div className="flex-1 p-8">
          {activeTab === "users" && <Users />}
          {activeTab === "requests" && <Requests />}
          {activeTab === "suspensions" && <Suspensions />}
          {activeTab === "books" && <Books />}
        </div>
      </div>
    </div>
  );
}
