import React, { useEffect, useState } from "react";
import axios from "axios";
import { Card, Spinner, Alert, ListGroup, Badge } from "react-bootstrap";
import { FaShieldAlt, FaLock, FaExclamationTriangle } from "react-icons/fa";

const SecurityOverview = () => {
  const [securityData, setSecurityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSecurity = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8010/security");
        setSecurityData(response.data);
      } catch (err) {
        setError("Failed to fetch security data");
      } finally {
        setLoading(false);
      }
    };

    fetchSecurity();
  }, []);

  return (
    <div>
      <h5 style={styles.title}>🛡️ Security Overview</h5>
      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}

      {securityData && (
        <Card style={styles.card}>
          <Card.Body>
            <Card.Title style={styles.cardTitle}>
              Current Security Posture
            </Card.Title>

            <ListGroup variant="flush">
              <ListGroup.Item>
                <strong>Compliance Score:</strong>{" "}
                <Badge
                  bg={
                    securityData.compliance_score >= 80 ? "success" : "danger"
                  }
                >
                  {securityData.compliance_score}%
                </Badge>
              </ListGroup.Item>

              <ListGroup.Item>
                <strong>Public Buckets:</strong>{" "}
                {securityData.public_buckets ? (
                  <Badge bg="danger">Exposed</Badge>
                ) : (
                  <Badge bg="success">Secure</Badge>
                )}
              </ListGroup.Item>

              <ListGroup.Item>
                <strong>Open Ports:</strong>{" "}
                {securityData.open_ports.length > 0
                  ? securityData.open_ports.join(", ")
                  : "None"}
              </ListGroup.Item>

              <ListGroup.Item>
                <strong>IAM Misconfiguration:</strong>{" "}
                {securityData.iam_misconfiguration ? (
                  <Badge bg="danger">Risk</Badge>
                ) : (
                  <Badge bg="success">Safe</Badge>
                )}
              </ListGroup.Item>

              <ListGroup.Item>
                <strong>Encryption Missing:</strong>{" "}
                {securityData.encryption_missing ? (
                  <Badge bg="danger">Missing</Badge>
                ) : (
                  <Badge bg="success">Enabled</Badge>
                )}
              </ListGroup.Item>

              <ListGroup.Item>
                <strong>MFA Missing:</strong>{" "}
                {securityData.mfa_missing ? (
                  <Badge bg="danger">Not Enforced</Badge>
                ) : (
                  <Badge bg="success">Enforced</Badge>
                )}
              </ListGroup.Item>

              <ListGroup.Item>
                <strong>Suspicious Logins:</strong>{" "}
                {securityData.suspicious_login_detected ? (
                  <Badge bg="danger">Detected</Badge>
                ) : (
                  <Badge bg="success">None</Badge>
                )}
              </ListGroup.Item>
            </ListGroup>

            <hr />

            <h6>🛠️ Recommendations:</h6>
            <ul>
              {securityData.recommendations.map((rec, index) => (
                <li key={index}>
                  <FaExclamationTriangle color="orange" /> {rec}
                </li>
              ))}
            </ul>
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
  cardTitle: {
    marginBottom: "10px",
    fontSize: "20px",
  },
};

export default SecurityOverview;
