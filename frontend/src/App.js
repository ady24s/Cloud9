import React, { useMemo, useState, useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import LoginPage from "./components/LoginPage.jsx";
import Dashboard from "./components/Dashboard";
import BudgetPage from "./components/BudgetPage";
import SecurityPage from "./components/SecurityPage";
import AuthSuccess from "./components/AuthSuccess";
import ChooseCloudPage from "./components/ChooseCloudPage";

const Protected = ({ children }) => {
  const token = localStorage.getItem("access_token");
  const location = useLocation();
  if (!token) return <Navigate to="/" replace state={{ from: location }} />;
  return children;
};

export default function App() {
  const [provider, setProvider] = useState(() => {
    return localStorage.getItem("cloud_provider") || "aws";
  });

  useEffect(() => {
    localStorage.setItem("cloud_provider", provider);
  }, [provider]);

  useMemo(() => process.env.REACT_APP_API_URL || "http://localhost:8000", []);

  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthSuccess />} />
      <Route path="/choose-cloud" element={<ChooseCloudPage setProvider={setProvider} />} />

      <Route
        path="/dashboard"
        element={
          <Protected>
            <Dashboard provider={provider} />
          </Protected>
        }
      />
      <Route
        path="/budget"
        element={
          <Protected>
            <BudgetPage provider={provider} />
          </Protected>
        }
      />
      <Route
        path="/security"
        element={
          <Protected>
            <SecurityPage provider={provider} />
          </Protected>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
