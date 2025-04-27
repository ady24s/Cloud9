import React from 'react';
import SecurityOverview from './SecurityOverview';
import SecurityTrend from './SecurityTrend';
import { Button, Row, Col, Card } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const SecurityPage = ({ provider }) => {
  const navigate = useNavigate();

  return (
    <div style={styles.pageWrapper}>
      {/* Top Navigation */}
      <div style={styles.navButtons}>
        <Button variant="primary" onClick={() => navigate('/dashboard')}>Dashboard</Button>
        <Button variant="secondary" onClick={() => navigate('/security')}>Security</Button>
        <Button variant="secondary" onClick={() => navigate('/budget')}>Budget</Button>
      </div>

      <h2>Security Overview</h2>

      <Row style={{ marginTop: '20px' }}>
        <Col md={6}>
          <Card style={styles.card}>
            <Card.Body>
              <Card.Title>Security Status</Card.Title>
              <SecurityOverview />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card style={styles.card}>
            <Card.Body>
              <Card.Title>Security Compliance Trend</Card.Title>
              <SecurityTrend />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

const styles = {
  pageWrapper: {
    padding: '30px',
    backgroundColor: '#f5f9ff',
    minHeight: '100vh',
    fontFamily: 'Arial, sans-serif',
  },
  navButtons: {
    marginBottom: '20px',
    display: 'flex',
    gap: '10px',
  },
  card: {
    marginBottom: '20px',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
    backgroundColor: '#ffffff',
  },
};

export default SecurityPage;
