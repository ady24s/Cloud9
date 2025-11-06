import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { Alert } from "react-bootstrap";
import api from "../api";

const SpendHistory = ({ provider }) => {
  const [data, setData] = useState([]);
  const [anomalyDetected, setAnomalyDetected] = useState(false);

  useEffect(() => {
    const fetchSpendData = async () => {
      try {
        const response = await api.get("/users/me/spend-series", {
          params: { 
            days: 180,
            provider // ✅ Added provider param
          }
        });
        const points = response.data?.points || [];
        const chartData = points.map((p) => ({ month: p.date, spend: p.spend }));

        setData(chartData);

        if (chartData.length >= 2) {
          const last = chartData[chartData.length - 2].spend || 0;
          const curr = chartData[chartData.length - 1].spend || 0;
          const spike = last > 0 ? ((curr - last) / last) * 100 : 0;
          if (spike > 25) setAnomalyDetected(true);
        }
      } catch (error) {
        console.error("Error fetching spend series:", error);
      }
    };

    fetchSpendData();
  }, [provider]); // ✅ Added provider dependency

  return (
    <div>
      <h5 style={styles.title}>📈 {provider.toUpperCase()} Spend History</h5>

      {anomalyDetected && (
        <Alert variant="danger">🚨 Anomaly Detected! Cost spike detected in {provider}!</Alert>
      )}

      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="spend" stroke="#dc3545" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const styles = {
  title: { marginBottom: "15px", fontWeight: "bold", color: "#333" },
};

export default SpendHistory;