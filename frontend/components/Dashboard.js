import React from 'react';
import SpendOverview from './SpendOverview';
import IdleResources from './IdleResources';
import ActiveInstances from './ActiveInstances';
import S3Buckets from './S3Buckets';

const Dashboard = () => {
  return (
    <div style={styles.dashboardWrapper}>
      <h1 style={styles.heading}>CloudWise: AI Powered Cloud Management System</h1>
      <div style={styles.gridContainer}>
        <div style={styles.gridItem}><ActiveInstances /></div>
        <div style={styles.gridItem}><S3Buckets /></div>
        <div style={styles.gridItem}><IdleResources /></div>
        <div style={styles.gridItem}><SpendOverview /></div>
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
    marginBottom: '30px',
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#333',
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
