import React, { useEffect, useState } from 'react';
import SpendOverview from './SpendOverview';
import ActiveInstances from './ActiveInstances';
import S3Buckets from './S3Buckets';
import IdleResources from './IdleResources';
import SpendHistory from './SpendHistory';
import axios from 'axios';
import { Card, Row, Col } from 'react-bootstrap';

const Dashboard = ({ provider }) => {  // ✅ Accept provider prop
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/metrics");
        setMetrics(response.data);
      } catch (error) {
        console.error("Error fetching metrics:", error);
      }
    };
    fetchMetrics();
  }, []);

  return (
    <div style={styles.dashboardWrapper}>
      <h1 style={styles.heading}>
        Cloud9 : AI Powered Cloud Management System ({provider.toUpperCase()} User)
      </h1>

      {/* Top Summary Cards */}
      {metrics && (
        <Row style={styles.summaryRow}>
          <Col md={4}>
            <Card style={styles.summaryCard}>
              <Card.Body>
                <Card.Title>Total Instances</Card.Title>
                <Card.Text style={styles.metricText}>{metrics.totalInstances || 15}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card style={styles.summaryCard}>
              <Card.Body>
                <Card.Title>Idle Resources</Card.Title>
                <Card.Text style={styles.metricText}>{metrics.idleResources}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card style={styles.summaryCard}>
              <Card.Body>
                <Card.Title>Predicted Savings</Card.Title>
                <Card.Text style={styles.metricText}>₹ {metrics.predictedSavings}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Main Grid */}
      <div style={styles.gridContainer}>
        {/* ✅ Pass provider prop down */}
        <div style={styles.gridItem}><ActiveInstances provider={provider} /></div>
        <div style={styles.gridItem}><S3Buckets provider={provider} /></div>
        <div style={styles.gridItem}><IdleResources /></div>
        <div style={styles.gridItem}><SpendOverview /></div>
        <div style={styles.gridItem}><SpendHistory /></div>
      </div>
    </div>
  );
};

const styles = {
  dashboardWrapper: {
    textAlign: 'center',
    backgroundColor: '#f5f9ff',
    minHeight: '100vh',
    padding: '30px 15px',
    fontFamily: 'Arial, sans-serif',
  },
  heading: {
    marginBottom: '20px',
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#333',
  },
  summaryRow: {
    marginBottom: '30px',
    paddingLeft: '20px',
    paddingRight: '20px',
  },
  summaryCard: {
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
    textAlign: 'center',
    backgroundColor: '#ffffff',
    marginBottom: '15px',
  },
  metricText: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#007bff',
  },
  gridContainer: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  gridItem: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  },
};

export default Dashboard;
