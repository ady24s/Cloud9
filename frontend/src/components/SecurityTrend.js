import React, { useEffect, useState } from "react";
import axios from "../api";
import { Spinner, Alert } from "react-bootstrap";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const SecurityTrend = ({ provider }) => {
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrend = async () => {
      try {
        setLoading(true);
        const res = await axios.get("/users/me/security/trend", {
          params: { provider } // ✅ Added provider param
        });
        setTrend(res.data.trend || []);
      } catch (err) {
        console.error("Error fetching trend:", err);
        setError("Failed to load security trend.");
      } finally {
        setLoading(false);
      }
    };
    fetchTrend();
  }, [provider]); // ✅ Added provider dependency

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (!trend || trend.length === 0) return <Alert variant="info">No trend data for {provider}.</Alert>;

  const chartData = {
    labels: trend.map((p) => p.date),
    datasets: [
      {
        label: `${provider.toUpperCase()} Compliance Score`,
        data: trend.map((p) => p.compliance_score),
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${provider.toUpperCase()} Security Compliance Trend`,
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

export default SecurityTrend;