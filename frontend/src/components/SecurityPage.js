import React from 'react';
import SecurityOverview from './SecurityOverview';
import SecurityTrend from './SecurityTrend';
import { Row, Col } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const SecurityPage = ({ provider }) => {
  const navigate = useNavigate();

  return (
    <div style={styles.pageWrapper}>
      <div style={styles.navbar}>
        <button style={{ ...styles.navButton, backgroundColor: '#0d6efd' }} onClick={() => navigate('/dashboard')}>
          Dashboard
        </button>
        <button style={{ ...styles.navButton, backgroundColor: '#0d6efd', opacity: 0.8 }} onClick={() => navigate('/security')}>
          Security
        </button>
        <button style={{ ...styles.navButton, backgroundColor: '#198754' }} onClick={() => navigate('/budget')}>
          Budget
        </button>
      </div>

      <h2 style={styles.heading}>🛡️ Cloud Security Center</h2>

      <Row style={styles.cardRow}>
        <Col md={6}>
          <div style={styles.card}>
            <h4 style={styles.cardTitle}>🔒 Security Overview</h4>
            <SecurityOverview />
          </div>
        </Col>
        <Col md={6}>
          <div style={styles.card}>
            <h4 style={styles.cardTitle}>📈 Compliance Trend</h4>
            <SecurityTrend />
          </div>
        </Col>
      </Row>
    </div>
  );
};

const styles = {
  pageWrapper: {
    minHeight: '100vh',
    padding: '40px 20px',
    background: 'linear-gradient(135deg, #0b2137 0%, #1f4368 50%, #1b365d 100%)',
    fontFamily: 'Inter, sans-serif',
    color: 'white',
  },
  navbar: { display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '30px' },
  navButton: {
    padding: '10px 25px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'transform 0.2s, opacity 0.2s',
  },
  heading: { textAlign: 'center', fontSize: '32px', fontWeight: '700', color: '#8FD3F4', marginBottom: '40px' },
  cardRow: { justifyContent: 'center', gap: '20px' },
  card: {
    background: 'rgba(255,255,255,0.05)',
    backdropFilter: 'blur(15px)',
    borderRadius: '20px',
    padding: '25px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
    transition: 'transform 0.3s, box-shadow 0.3s',
  },
  cardTitle: { fontSize: '22px', fontWeight: '600', color: '#8FD3F4', textAlign: 'center', marginBottom: '20px' },
};

export default SecurityPage;
