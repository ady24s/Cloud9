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

import awsLogo from "../assets/aws.png";
import googleLogo from "../assets/google-cloud.png";
import azureLogo from "../assets/azure.jpeg";

const PROVIDERS = {
  aws: { name: "AWS Cloud", logo: awsLogo },
  gcp: { name: "Google Cloud", logo: googleLogo },
  azure: { name: "Microsoft Azure", logo: azureLogo },
};

const Dashboard = ({ provider = "aws", setProvider }) => {
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
  }, [provider]); // Re-fetch when provider changes

  return (
    <div style={styles.pageWrapper}>
      <div style={styles.header}>
        {providerLogo && <img src={providerLogo} alt="Logo" style={styles.logo} />}
        <h1 style={styles.heading}>Cloud9 Dashboard — {providerName}</h1>
        
        {/* Navigation Buttons */}
        <div style={styles.navButtons}>
          <Button
            variant="primary"
            style={styles.navButton}
            onClick={() => navigate("/dashboard")}
          >
            🏠 Dashboard
          </Button>
          <Button
            variant="success"
            style={styles.navButton}
            onClick={() => navigate("/budget")}
          >
            💰 Budget
          </Button>
          <Button
            variant="warning"
            style={styles.navButton}
            onClick={() => navigate("/security")}
          >
            🛡️ Security
          </Button>
        </div>

        {/* Provider Switcher */}
        <div style={styles.providerSwitcher}>
          <select 
            value={provider} 
            onChange={(e) => setProvider(e.target.value)}
            style={styles.providerSelect}
          >
            <option value="aws">AWS</option>
            <option value="azure">Azure</option>
            <option value="gcp">GCP</option>
          </select>
        </div>

        <Button
          variant="danger"
          style={styles.logoutBtn}
          onClick={() => {
            localStorage.removeItem("cloud9_token");
            localStorage.removeItem("current_provider");
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
                <p>${metrics.total_spend}</p>
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
                <p>${metrics.predicted_savings}</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      ) : (
        <p>No metrics available.</p>
      )}

      <Row className="mt-4">
        <Col md={6}><SpendOverview provider={provider} /></Col>
        <Col md={6}><SpendHistory provider={provider} /></Col>
      </Row>

      <Row className="mt-4">
        <Col md={6}><ActiveInstances provider={provider} /></Col>
        <Col md={6}><IdleResources provider={provider} /></Col>
      </Row>

      <Row className="mt-4">
        <Col md={6}><SecurityOverview provider={provider} /></Col>
        <Col md={6}><SecurityTrend provider={provider} /></Col>
      </Row>

      {/* ChatbotUI row has been removed */}
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
  header: { 
    textAlign: "center", 
    marginBottom: "20px", 
    position: "relative" 
  },
  logo: { 
    width: 80, 
    marginBottom: 10 
  },
  heading: { 
    fontSize: "28px", 
    fontWeight: "700",
    marginBottom: "15px"
  },
  navButtons: {
    display: "flex",
    gap: "10px",
    marginBottom: "20px",
    justifyContent: "center"
  },
  navButton: {
    padding: "8px 16px",
    fontSize: "14px",
    fontWeight: "600"
  },
  providerSwitcher: {
    position: "absolute",
    top: 10,
    right: 100,
  },
  providerSelect: {
    padding: "5px 10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    background: "white",
    color: "black",
    fontSize: "14px",
  },
  logoutBtn: { 
    position: "absolute", 
    top: 0, 
    right: 20, 
    fontSize: "14px", 
    padding: "5px 10px" 
  },
  center: { 
    display: "flex", 
    justifyContent: "center", 
    marginTop: "20px" 
  },
  metricRow: { 
    marginTop: "20px" 
  },
  metricCard: {
    textAlign: "center",
    background: "rgba(255,255,255,0.05)",
    color: "white",
    border: "none",
    borderRadius: "15px",
  },
};

export default Dashboard;