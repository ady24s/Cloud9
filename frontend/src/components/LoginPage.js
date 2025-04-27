import React from 'react';
import { useNavigate } from 'react-router-dom'; // Updated for React Router v7
import googleLogo from '../assets/google-cloud.png';
import azureLogo from '../assets/azure.jpeg';
import awsLogo from '../assets/aws.png';

const LoginPage = ({ setProvider }) => {
  const navigate = useNavigate(); // Now correct

  const handleLogin = (provider) => {
    setProvider(provider);
    localStorage.setItem('provider', provider);
    navigate('/dashboard');
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Welcome to Cloud9 ☁️</h2>
        <p style={styles.subtitle}>Manage your AWS, Azure, and GCP resources smartly.</p>

        <div style={styles.buttonGroup}>
          <button style={styles.loginButton} onClick={() => handleLogin('gcp')}>
            <img src={googleLogo} alt="Google Cloud" style={styles.logo} />
            Sign in with Google Cloud
          </button>

          <button style={{ ...styles.loginButton, backgroundColor: '#0078D4' }} onClick={() => handleLogin('azure')}>
            <img src={azureLogo} alt="Microsoft Azure" style={styles.logo} />
            Sign in with Microsoft Azure
          </button>

          <button style={{ ...styles.loginButton, backgroundColor: '#FF9900' }} onClick={() => handleLogin('aws')}>
            <img src={awsLogo} alt="AWS" style={styles.logo} />
            Sign in with AWS
          </button>
        </div>

        <p style={styles.footer}>Cloud9 works seamlessly across all major cloud platforms.</p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    background: 'linear-gradient(to bottom right, #e6f0ff, #f5f9ff)',
    fontFamily: 'Arial, sans-serif',
  },
  card: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '12px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
    textAlign: 'center',
    maxWidth: '400px',
  },
  title: {
    fontSize: '2rem',
    fontWeight: 'bold',
    marginBottom: '10px',
  },
  subtitle: {
    fontSize: '1rem',
    color: '#666',
    marginBottom: '30px',
  },
  buttonGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    marginBottom: '20px',
  },
  loginButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    backgroundColor: '#4285F4',
    color: 'white',
    border: 'none',
    padding: '12px 20px',
    borderRadius: '8px',
    fontSize: '16px',
    cursor: 'pointer',
    justifyContent: 'center',
  },
  logo: {
    width: '24px',
    height: '24px',
  },
  footer: {
    fontSize: '0.9rem',
    color: '#888',
    marginTop: '20px',
  },
};

export default LoginPage;
