import React, { useEffect, useState } from "react";
import axios from "../api";
import { Card, Alert, Spinner } from "react-bootstrap";

const SecurityOverview = ({ provider }) => {
  const [security, setSecurity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSecurity = async () => {
      try {
        setLoading(true);
        const res = await axios.get("/users/me/security", {
          params: { provider } // ✅ Added provider param
        });
        setSecurity(res.data);
      } catch (err) {
        console.error("Error fetching security overview:", err);
        setError("Failed to load security posture.");
      } finally {
        setLoading(false);
      }
    };
    fetchSecurity();
  }, [provider]); // ✅ Added provider dependency

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!security) return <Alert variant="info">No security data available for {provider}.</Alert>;

  return (
    <Card className="p-3">
      <h5>🔒 {provider.toUpperCase()} Security Overview</h5>
      <p>Compliance Score: {security.compliance_score}%</p>
      <p>Public Resources: {security.public_buckets ? "Yes" : "No"}</p>
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