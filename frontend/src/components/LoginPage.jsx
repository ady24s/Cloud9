import React from "react";
import { Button, Container, Row, Col } from "react-bootstrap";

// Full-page redirect must use backend origin, not relative path.
const BACKEND_ORIGIN =
  process.env.REACT_APP_BACKEND_ORIGIN ||
  `${window.location.protocol}//${window.location.hostname}:8000`;

const LoginPage = () => {
  const handleLogin = (idp) => {
    if (idp === "google") {
      window.location.href = `${BACKEND_ORIGIN}/auth/google/login`;
    } else if (idp === "microsoft") {
      window.location.href = `${BACKEND_ORIGIN}/auth/microsoft/login`;
    }
  };

  return (
    <Container
      className="d-flex flex-column justify-content-center align-items-center"
      style={{ height: "100vh" }}
    >
      <Row>
        <h2>Welcome to Cloud9</h2>
        <p>Sign in to get started</p>
      </Row>
      <Row className="mt-3">
        <Col>
          <Button
            variant="primary"
            onClick={() => handleLogin("google")}
            className="mb-3 w-100"
          >
            Continue with Google
          </Button>
        </Col>
      </Row>
      <Row>
        <Col>
          <Button
            variant="dark"
            onClick={() => handleLogin("microsoft")}
            className="w-100"
          >
            Continue with Microsoft
          </Button>
        </Col>
      </Row>
    </Container>
  );
};

export default LoginPage;
