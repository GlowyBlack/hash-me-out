"use client";

import LoginForm from "../Forms/LoginForm";
import RegisterForm from "../Forms/RegisterForm";

export default function AuthPopup({ formType, setFormType, handleLoginSuccess }) {
  if (!formType) return null;

  return (
    <div className="absolute top-20 right-6 z-50">
      <div className="bg-white p-4 rounded-xl shadow-xl w-80">
        {formType === "login" && (
          <LoginForm setFormType={setFormType} onSuccess={handleLoginSuccess} />
        )}

        {formType === "register" && (
          <RegisterForm setFormType={setFormType} onSuccess={handleLoginSuccess} />
        )}
      </div>
    </div>
  );
}
