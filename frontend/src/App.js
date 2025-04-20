import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import LoginPage from './components/LoginPage';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  const [provider, setProvider] = useState(null);

  useEffect(() => {
    const savedProvider = localStorage.getItem('provider');
    if (savedProvider) {
      setProvider(savedProvider);
    }
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage setProvider={setProvider} />} />
        <Route path="/dashboard" element={provider ? <Dashboard provider={provider} /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
