import React, { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Row, Col, Button, Spinner, Alert } from "react-bootstrap";
import api from "../api";
import SpendOverview from "./SpendOverview";
import SpendHistory from "./SpendHistory";
import ActiveInstances from "./ActiveInstances";
import IdleResources from "./IdleResources";
import SecurityOverview from "./SecurityOverview";
import SecurityTrend from "./SecurityTrend";
import ChatbotUI from "./ChatbotUI";

import awsLogo from "../assets/aws.png";
import googleLogo from "../assets/google-cloud.png";
import azureLogo from "../assets/azure.jpeg";

const PROVIDERS = {
  aws: { name: "AWS Cloud", logo: awsLogo },
  gcp: { name: "Google Cloud", logo: googleLogo },
  azure: { name: "Microsoft Azure", logo: azureLogo },
};

const Dashboard = ({ provider = "aws" }) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  const token = localStorage.getItem("cloud9_token");

  useEffect(() => {
    if (!token) navigate("/");
  }, [token, navigate]);

  const { name: providerName, logo: providerLogo } = useMemo(() => {
    return PROVIDERS[provider] || { name: "Unknown Provider", logo: null };
  }, [provider]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const res = await api.get("/users/me/insights");
        setMetrics(res.data);
      } catch (error) {
        console.error("Error fetching insights:", error);
        setErr("Unable to fetch metrics from server.");
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  return (
    <div style={styles.pageWrapper}>
      <div style={styles.header}>
        {providerLogo && <img src={providerLogo} alt="Logo" style={styles.logo} />}
        <h1 style={styles.heading}>Cloud9 Dashboard — {providerName}</h1>
        <Button
          variant="danger"
          style={styles.logoutBtn}
          onClick={() => {
            localStorage.removeItem("cloud9_token");
            navigate("/");
          }}
        >
          Logout
        </Button>
      </div>

      {err && <Alert variant="danger">{err}</Alert>}

      {loading ? (
        <div style={styles.center}>
          <Spinner animation="border" />
        </div>
      ) : metrics ? (
        <Row style={styles.metricRow}>
          <Col md={4}>
            <Card style={styles.metricCard}>
              <Card.Body>
                <h5>Total Spend</h5>
                <p>{metrics.total_spend}</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card style={styles.metricCard}>
              <Card.Body>
                <h5>Idle Resources</h5>
                <p>{metrics.idle_resources}</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card style={styles.metricCard}>
              <Card.Body>
                <h5>Predicted Savings</h5>
                <p>{metrics.predicted_savings}</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ) : (
        <p>No metrics available.</p>
      )}

      <Row className="mt-4">
        <Col md={6}><SpendOverview /></Col>
        <Col md={6}><SpendHistory /></Col>
      </Row>

      <Row className="mt-4">
        <Col md={6}><ActiveInstances provider={provider} /></Col>
        <Col md={6}><IdleResources /></Col>
      </Row>

      <Row className="mt-4">
        <Col md={6}><SecurityOverview /></Col>
        <Col md={6}><SecurityTrend /></Col>
      </Row>

      <Row className="mt-4">
        <Col md={12}><ChatbotUI /></Col>
      </Row>
    </div>
  );
};

const styles = {
  pageWrapper: {
    minHeight: "100vh",
    padding: "20px",
    background: "linear-gradient(135deg, #0b2137 0%, #1f4368 50%, #1b365d 100%)",
    color: "white",
    fontFamily: "Inter, sans-serif",
  },
  header: { textAlign: "center", marginBottom: "20px", position: "relative" },
  logo: { width: 80, marginBottom: 10 },
  heading: { fontSize: "28px", fontWeight: "700" },
  logoutBtn: { position: "absolute", top: 0, right: 20, fontSize: "14px", padding: "5px 10px" },
  center: { display: "flex", justifyContent: "center", marginTop: "20px" },
  metricRow: { marginTop: "20px" },
  metricCard: {
    textAlign: "center",
    background: "rgba(255,255,255,0.05)",
    color: "white",
    border: "none",
    borderRadius: "15px",
  },
};

export default Dashboard;
