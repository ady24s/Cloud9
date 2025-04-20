import React from 'react';
import { useNavigate } from 'react-router-dom';

const LoginPage = ({ setProvider }) => {
  const navigate = useNavigate();

  const handleLogin = (provider) => {
    setProvider(provider);  // Save provider name (AWS, GCP, Azure)
    localStorage.setItem('provider', provider);  // Optional persistence
    navigate('/dashboard');  // Redirect to Dashboard
  };

  return (
    <div style={styles.loginContainer}>
      <h2 style={styles.title}>Welcome to Cloud9 ☁️</h2>
      <p style={styles.subtitle}>Choose your Cloud Provider to continue</p>

      <div style={styles.buttonContainer}>
        <button style={styles.googleBtn} onClick={() => handleLogin('gcp')}>Login with Google Cloud</button>
        <button style={styles.azureBtn} onClick={() => handleLogin('azure')}>Login with Microsoft Azure</button>
        <button style={styles.awsBtn} onClick={() => handleLogin('aws')}>Login with AWS</button>
      </div>
    </div>
  );
};

const styles = {
  loginContainer: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    background: 'linear-gradient(to bottom right, #d8eafd, #f0f4ff)',
    fontFamily: 'Arial, sans-serif',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#333',
  },
  subtitle: {
    fontSize: '1.2rem',
    marginBottom: '30px',
    color: '#666',
  },
  buttonContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  googleBtn: {
    backgroundColor: '#4285F4',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    width: '250px',
  },
  azureBtn: {
    backgroundColor: '#0078D4',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    width: '250px',
  },
  awsBtn: {
    backgroundColor: '#FF9900',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    width: '250px',
  },
};

export default LoginPage;
