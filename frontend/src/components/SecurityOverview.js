import React, { useEffect, useState } from 'react';
import { Card, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { FaExclamationTriangle, FaLock } from 'react-icons/fa';

const SecurityOverview = () => {
  const [securityData, setSecurityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSecurityData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/security');
        setSecurityData(response.data);
      } catch (error) {
        console.error('Error fetching security data:', error);
        setError('Failed to load security data');
      } finally {
        setLoading(false);
      }
    };

    fetchSecurityData();
  }, []);

  return (
    <div>
      <h5 style={styles.title}>🔒 Security Overview</h5>

      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}

      {securityData && (
        <Card style={securityData.issues_found > 0 ? styles.alertCard : styles.safeCard}>
          <Card.Body>
            {securityData.issues_found > 0 ? (
              <>
                <FaExclamationTriangle style={{ color: 'red', fontSize: '30px', marginBottom: '10px' }} />
                <Card.Title style={{ color: 'red' }}>Risks Detected</Card.Title>
                <Card.Text>
                  Public Buckets: {securityData.public_buckets} <br />
                  Exposed Ports: {securityData.open_ports.join(', ') || 'None'} <br />
                  Recommendation: {securityData.recommendation}
                </Card.Text>
              </>
            ) : (
              <>
                <FaLock style={{ color: 'green', fontSize: '30px', marginBottom: '10px' }} />
                <Card.Title style={{ color: 'green' }}>All Good!</Card.Title>
                <Card.Text>No major security risks detected.</Card.Text>
              </>
            )}
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

const styles = {
  title: {
    marginBottom: '15px',
    fontWeight: 'bold',
    color: '#333',
  },
  alertCard: {
    backgroundColor: '#ffe6e6',
    borderColor: 'red',
    borderRadius: '12px',
    boxShadow: '0 4px 8px rgba(255, 0, 0, 0.2)',
    padding: '20px',
  },
  safeCard: {
    backgroundColor: '#e6ffe6',
    borderColor: 'green',
    borderRadius: '12px',
    boxShadow: '0 4px 8px rgba(0, 255, 0, 0.2)',
    padding: '20px',
  },
};

export default SecurityOverview;
