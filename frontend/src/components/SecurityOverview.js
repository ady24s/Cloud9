// src/components/SecurityOverview.js
import React, { useEffect, useState } from "react";
import axios from "../api";
import { Card, Alert, Spinner } from "react-bootstrap";

const SecurityOverview = () => {
  const [security, setSecurity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSecurity = async () => {
      try {
        setLoading(true);
        const res = await axios.get("/users/me/security");
        setSecurity(res.data);
      } catch (err) {
        console.error("Error fetching security overview:", err);
        setError("Failed to load security posture.");
      } finally {
        setLoading(false);
      }
    };
    fetchSecurity();
  }, []);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!security) return <Alert variant="info">No data available.</Alert>;

  return (
    <Card className="p-3">
      <h5>Compliance Score: {security.compliance_score}%</h5>
      <p>Public Buckets: {security.public_buckets ? "Yes" : "No"}</p>
      <p>MFA Missing: {security.mfa_missing ? "Yes" : "No"}</p>
      <h6>Recommendations:</h6>
      <ul>
        {security.recommendations.map((r, i) => (
          <li key={i}>{r}</li>
        ))}
      </ul>
    </Card>
  );
};

export default SecurityOverview;
