// src/components/SecurityTrend.js
import React, { useEffect, useState } from "react";
import axios from "../api";
import { Spinner, Alert } from "react-bootstrap";
import { Line } from "react-chartjs-2";

const SecurityTrend = () => {
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrend = async () => {
      try {
        setLoading(true);
        const res = await axios.get("/users/me/security/trend");
        setTrend(res.data.trend || []);
      } catch (err) {
        console.error("Error fetching trend:", err);
        setError("Failed to load security trend.");
      } finally {
        setLoading(false);
      }
    };
    fetchTrend();
  }, []);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;

  const chartData = {
    labels: trend.map((p) => p.date),
    datasets: [
      {
        label: "Compliance Score",
        data: trend.map((p) => p.compliance_score),
        fill: false,
        borderColor: "blue",
        tension: 0.1,
      },
    ],
  };

  return <Line data={chartData} />;
};

export default SecurityTrend;
