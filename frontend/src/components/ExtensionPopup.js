import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, Button, Spinner, Alert } from "react-bootstrap";
import {
  FaMoneyBillWave,
  FaServer,
  FaExclamationTriangle,
  FaRobot,
  FaExternalLinkAlt,
  FaLockOpen,
} from "react-icons/fa";

const ExtensionPopup = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8010/metrics")
      .then((response) => {
        setMetrics(response.data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to fetch data");
        setLoading(false);
      });
  }, []);

  return (
    <div style={styles.popupContainer}>
      <h5 style={styles.title}>Cloud AI Optimizer</h5>

      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}

      {metrics && (
        <div style={styles.scrollableContent}>
          {/* Cloud Spend Overview */}
          <Card style={styles.card}>
            <Card.Body style={styles.cardRow}>
              <FaMoneyBillWave style={{ ...styles.icon, color: "#28a745" }} />
              <div>
                <Card.Title style={styles.cardTitle}>💰 Cloud Spend</Card.Title>
                <Card.Text style={styles.cardText}>
                  ${metrics.totalSpend}{" "}
                  <span style={{ color: "green" }}>⬆️ 12%</span>
                </Card.Text>
              </div>
            </Card.Body>
          </Card>

          {/* Idle Resources */}
          <Card
            style={styles.clickableCard}
            onClick={() =>
              window.open("http://localhost:3000/idle-resources", "_blank")
            }
          >
            <Card.Body style={styles.cardRow}>
              <FaServer style={{ ...styles.icon, color: "#007bff" }} />
              <div>
                <Card.Title style={styles.cardTitle}>
                  💤 Idle Instances
                </Card.Title>
                <Card.Text style={styles.cardText}>
                  {metrics.idleResources} (Click to View)
                </Card.Text>
              </div>
            </Card.Body>
          </Card>

          {/* Anomalies */}
          <Card style={styles.card}>
            <Card.Body style={styles.cardRow}>
              <FaExclamationTriangle
                style={{ ...styles.icon, color: "#dc3545" }}
              />
              <div>
                <Card.Title style={styles.cardTitle}>
                  ⚠️ Anomalies Detected
                </Card.Title>
                <Card.Text style={styles.cardText}>
                  Cost Spike: +$500
                  <br />
                  <FaLockOpen style={{ color: "red" }} /> Public S3 Bucket
                </Card.Text>
              </div>
            </Card.Body>
          </Card>

          {/* AI Insights */}
          <Card style={{ ...styles.card, backgroundColor: "#e3fcef" }}>
            <Card.Body style={styles.cardRow}>
              <FaRobot style={{ ...styles.icon, color: "#17a2b8" }} />
              <div>
                <Card.Title style={styles.cardTitle}>🤖 AI Insights</Card.Title>
                <Card.Text style={styles.cardText}>
                  Stop 3 instances → Save ${metrics.predictedSavings}
                </Card.Text>
              </div>
            </Card.Body>
          </Card>

          {/* Open Full Dashboard */}
          <Button
            variant="primary"
            style={styles.fullDashboardButton}
            onClick={() => window.open("http://localhost:3000/", "_blank")}
          >
            🔗 Open Full Dashboard <FaExternalLinkAlt />
          </Button>
        </div>
      )}
    </div>
  );
};

const styles = {
  popupContainer: {
    width: "320px",
    height: "500px",
    backgroundColor: "#e7f3ff",
    padding: "15px",
    display: "flex",
    flexDirection: "column",
  },
  title: {
    textAlign: "center",
    fontWeight: "bold",
    marginBottom: "10px",
    color: "#333",
  },
  scrollableContent: {
    overflowY: "auto",
    maxHeight: "430px",
    paddingRight: "5px",
  },
  card: {
    marginBottom: "10px",
    borderRadius: "10px",
    border: "none",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
  },
  clickableCard: {
    marginBottom: "10px",
    borderRadius: "10px",
    border: "none",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    cursor: "pointer",
  },
  cardRow: {
    display: "flex",
    alignItems: "center",
  },
  cardTitle: {
    fontSize: "16px",
    marginBottom: "5px",
  },
  cardText: {
    fontSize: "14px",
    color: "#555",
  },
  icon: {
    fontSize: "30px",
    marginRight: "10px",
  },
  fullDashboardButton: {
    marginTop: "5px",
    width: "100%",
  },
};

export default ExtensionPopup;
