// src/components/Optimizer.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Card, Table, Spinner, Alert } from "react-bootstrap";

const Optimizer = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchOptimizerData = async () => {
      try {
        const response = await axios.post("http://127.0.0.1:8010/optimizer");
        setRecommendations(response.data.recommendations);
      } catch (err) {
        setError("Failed to fetch optimization data");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchOptimizerData();
  }, []);

  if (loading) {
    return (
      <div style={styles.wrapper}>
        <Spinner animation="border" variant="primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.wrapper}>
        <Alert variant="danger">{error}</Alert>
      </div>
    );
  }

  return (
    <div style={styles.wrapper}>
      <h2 style={styles.heading}>
        Cloud Resource Optimization Recommendations
      </h2>

      <Card style={styles.card}>
        <Card.Body>
          <Card.Title>Recommendations</Card.Title>
          <Table striped bordered hover responsive>
            <thead>
              <tr>
                <th>Resource ID</th>
                <th>Cluster ID</th>
                <th>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {recommendations.map((rec, idx) => (
                <tr key={idx}>
                  <td>{rec.resource_id}</td>
                  <td>{rec.cluster_id}</td>
                  <td>{rec.recommendation}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </div>
  );
};

const styles = {
  wrapper: {
    padding: "30px 20px",
    backgroundColor: "#f5f9ff",
    minHeight: "100vh",
    fontFamily: "Arial, sans-serif",
    textAlign: "center",
  },
  heading: {
    fontWeight: "bold",
    marginBottom: "30px",
  },
  card: {
    marginTop: "20px",
  },
};

export default Optimizer;
