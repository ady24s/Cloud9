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
import { Spinner, Alert, Card } from "react-bootstrap";

const SecurityTrend = () => {
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrend = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8010/security/trend"
        );
        setTrendData(response.data);
      } catch (err) {
        setError("Failed to fetch security trend data");
      } finally {
        setLoading(false);
      }
    };

    fetchTrend();
  }, []);

  return (
    <div>
      <h5 style={styles.title}>📈 Security Compliance Trend</h5>
      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}

      {!loading && !error && (
        <Card style={styles.card}>
          <Card.Body>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[50, 100]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="compliance_score"
                  stroke="#28a745"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

const styles = {
  title: {
    marginBottom: "15px",
    fontWeight: "bold",
    color: "#333",
  },
  card: {
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
    padding: "10px",
  },
};

export default SecurityTrend;
