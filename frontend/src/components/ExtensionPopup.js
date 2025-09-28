import React, { useState } from "react";
import { Card, Form, Button, Alert } from "react-bootstrap";
import api from "../api";
import { useNavigate } from "react-router-dom";

const ExtensionPopup = () => {
  const [provider, setProvider] = useState("aws");
  const [accessKey, setAccessKey] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [extraJSON, setExtraJSON] = useState("");
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setOk("");

    try {
      const payload = {
        provider,
        access_key: accessKey,
        secret_key: secretKey,
        extra_json: extraJSON || "{}",
      };
      await api.post("/credentials", payload);
      setOk("Credentials saved. Redirecting to dashboard…");
      setTimeout(() => navigate("/dashboard"), 800);
    } catch (err) {
      console.error(err);
      setError("Failed to save credentials.");
    }
  };

  return (
    <div style={styles.page}>
      <Card style={styles.card}>
        <Card.Body>
          <Card.Title>Connect Your Cloud Account</Card.Title>
          <Form onSubmit={onSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Provider</Form.Label>
              <Form.Select value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="aws">AWS</option>
                <option value="gcp">Google Cloud</option>
                <option value="azure">Microsoft Azure</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Access Key / Client ID</Form.Label>
              <Form.Control
                value={accessKey}
                onChange={(e) => setAccessKey(e.target.value)}
                placeholder="AKIA... or client id"
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Secret Key / Client Secret</Form.Label>
              <Form.Control
                value={secretKey}
                onChange={(e) => setSecretKey(e.target.value)}
                placeholder="secret..."
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Extra JSON (optional)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={extraJSON}
                onChange={(e) => setExtraJSON(e.target.value)}
                placeholder='{"region":"us-east-1"}'
              />
            </Form.Group>

            <Button type="submit">Save & Continue</Button>
          </Form>
          {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
          {ok && <Alert variant="success" className="mt-3">{ok}</Alert>}
        </Card.Body>
      </Card>
    </div>
  );
};

const styles = {
  page: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" },
  card: { width: 520 },
};

export default ExtensionPopup;
