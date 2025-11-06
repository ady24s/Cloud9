// frontend/src/components/AuthSuccess.jsx
import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

export default function AuthSuccess() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Parse token from URL query param
    const params = new URLSearchParams(location.search);
    const token = params.get("token");

    if (token) {
      // ✅ Store token in a consistent key
      localStorage.setItem("cloud9_token", token);

      // Optional: you can also store login timestamp
      localStorage.setItem("login_time", Date.now().toString());

      // Redirect to choose-cloud page
      navigate("/choose-cloud", { replace: true });
    } else {
      alert("Login failed. No token received.");
      navigate("/", { replace: true });
    }
  }, [location, navigate]);

  return <p>Processing login, please wait...</p>;
}
