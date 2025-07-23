import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Alert } from "react-bootstrap";

const SpendHistory = () => {
  const [data, setData] = useState([]);
  const [anomalyDetected, setAnomalyDetected] = useState(false);

  useEffect(() => {
    const fetchSpendData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8010/spend-history");
        const months = response.data.months;
        const spend = response.data.spend;

        const chartData = months.map((month, index) => ({
          month,
          spend: spend[index],
        }));

        setData(chartData);

        // Simple Anomaly Detection
        if (spend.length >= 2) {
          const lastMonthSpend = spend[spend.length - 2];
          const currentMonthSpend = spend[spend.length - 1];

          const spike =
            ((currentMonthSpend - lastMonthSpend) / lastMonthSpend) * 100;

          if (spike > 25) {
            // Spike greater than 25%
            setAnomalyDetected(true);
          }
        }
      } catch (error) {
        console.error("Error fetching spend history:", error);
      }
    };

    fetchSpendData();
  }, []);

  return (
    <div>
      <h5 style={styles.title}>📈 Cloud Spend History (6 Months)</h5>

      {anomalyDetected && (
        <Alert variant="danger">
          🚨 Anomaly Detected! Cost Spike Detected This Month!
        </Alert>
      )}

      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="spend"
              stroke="#dc3545"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const styles = {
  title: {
    marginBottom: "15px",
    fontWeight: "bold",
    color: "#333",
  },
};

export default SpendHistory;
