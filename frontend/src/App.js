// App.js
import React, { useMemo, useState, useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import LoginPage from "./components/LoginPage.jsx";
import Dashboard from "./components/Dashboard";
import BudgetPage from "./components/BudgetPage";
import SecurityPage from "./components/SecurityPage";
import AuthSuccess from "./components/AuthSuccess";
import ChooseCloudPage from "./components/ChooseCloudPage";

const Protected = ({ children }) => {
  const token = localStorage.getItem("cloud9_token");
  const location = useLocation();
  if (!token) return <Navigate to="/" replace state={{ from: location }} />;
  return children;
};

export default function App() {
  const [currentProvider, setCurrentProvider] = useState(() => {
    return localStorage.getItem("current_provider") || "aws";
  });

  // Save provider to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("current_provider", currentProvider);
  }, [currentProvider]);

  useMemo(() => process.env.REACT_APP_API_URL || "http://localhost:8000", []);

  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthSuccess />} />
      <Route 
        path="/choose-cloud" 
        element={<ChooseCloudPage setCurrentProvider={setCurrentProvider} />} 
      />

      <Route
        path="/dashboard"
        element={
          <Protected>
            <Dashboard 
              provider={currentProvider} 
              setProvider={setCurrentProvider}
            />
          </Protected>
        }
      />
      <Route
        path="/budget"
        element={
          <Protected>
            <BudgetPage provider={currentProvider} />
          </Protected>
        }
      />
      <Route
        path="/security"
        element={
          <Protected>
            <SecurityPage provider={currentProvider} />
          </Protected>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}