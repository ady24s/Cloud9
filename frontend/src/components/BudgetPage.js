import React from 'react';
import SpendOverview from './SpendOverview';
import SpendHistory from './SpendHistory';
import { Row, Col } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const BudgetPage = ({ provider }) => {
  const navigate = useNavigate();

  return (
    <div style={styles.pageWrapper}>
      <h2 style={styles.heading}>💰 Budget Monitoring</h2>

      <div style={styles.navbar}>
        <button style={styles.primaryButton} onClick={() => navigate('/dashboard')}>
          Dashboard
        </button>
        <button style={styles.secondaryButton} onClick={() => navigate('/security')}>
          Security
        </button>
        <button
          style={{ ...styles.secondaryButton, backgroundColor: '#198754' }}
          onClick={() => navigate('/budget')}
        >
          Budget
        </button>
      </div>

      <Row style={styles.cardRow}>
        <Col md={6}>
          <div style={styles.card}>
            <h4 style={styles.cardTitle}>💵 Spend Overview</h4>
            <SpendOverview />
          </div>
        </Col>
        <Col md={6}>
          <div style={styles.card}>
            <h4 style={styles.cardTitle}>📊 Spend History</h4>
            <SpendHistory />
          </div>
        </Col>
      </Row>
    </div>
  );
};

const styles = {
  pageWrapper: {
    minHeight: '100vh',
    padding: '30px 20px',
    background: 'linear-gradient(135deg, #0b2137 0%, #1f4368 50%, #1b365d 100%)',
    fontFamily: 'Inter, sans-serif',
    color: 'white',
  },
  heading: {
    textAlign: 'center',
    fontSize: '32px',
    fontWeight: '700',
    color: '#8FD3F4',
    marginBottom: '20px',
  },
  navbar: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '40px',
  },
  primaryButton: {
    backgroundColor: '#0d6efd',
    border: 'none',
    padding: '10px 20px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    borderRadius: '10px',
    cursor: 'pointer',
    boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
    transition: 'transform 0.2s',
  },
  secondaryButton: {
    backgroundColor: 'rgba(255,255,255,0.08)',
    border: '1px solid rgba(255,255,255,0.2)',
    padding: '10px 20px',
    fontSize: '16px',
    fontWeight: '500',
    color: 'white',
    borderRadius: '10px',
    cursor: 'pointer',
    boxShadow: '0 4px 10px rgba(0,0,0,0.3)',
    transition: 'transform 0.2s, background-color 0.2s',
  },
  cardRow: { justifyContent: 'center', gap: '20px' },
  card: {
    background: 'rgba(255,255,255,0.05)',
    backdropFilter: 'blur(15px)',
    borderRadius: '20px',
    padding: '25px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
    transition: 'transform 0.3s, box-shadow 0.3s',
  },
  cardTitle: {
    fontSize: '22px',
    fontWeight: '600',
    color: '#8FD3F4',
    textAlign: 'center',
    marginBottom: '20px',
  },
};

export default BudgetPage;
