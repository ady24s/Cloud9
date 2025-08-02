import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, Spinner, Alert } from "react-bootstrap";

const IdleResources = () => {
  const [idleResources, setIdleResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchIdleResources = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8010/ai/idle-detection"
        );
        setIdleResources(response.data.idle_resources);
      } catch (err) {
        setError("Failed to fetch idle resources");
      } finally {
        setLoading(false);
      }
    };

    fetchIdleResources();
  }, []);

  return (
    <div>
      <h5>💤 Detected Idle Resources</h5>
      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}
      {!loading && !error && idleResources.length === 0 && (
        <p>No idle resources found.</p>
      )}
      {!loading && !error && idleResources.length > 0 && (
        <div style={{ maxHeight: "400px", overflowY: "auto" }}>
          <Table striped bordered hover responsive>
            <thead
              style={{
                position: "sticky",
                top: 0,
                background: "#f8f9fa",
                zIndex: 1,
              }}
            >
              <tr>
                <th>ID</th>
                <th>Resource Type</th>
                <th>CPU Usage (%)</th>
                <th>Memory Usage (%)</th>
                <th>Uptime (hrs)</th>
                <th>Network In (MB)</th>
                <th>Disk Read (MB)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {idleResources.map((instance) => (
                <tr key={instance.id}>
                  <td>{instance.id}</td>
                  <td>{instance.resource_type}</td>
                  <td>{instance.cpu_usage}</td>
                  <td>{instance.memory_usage}</td>
                  <td>{instance.uptime}</td>
                  <td>{instance.network_in}</td>
                  <td>{instance.disk_read}</td>
                  <td>{instance.status}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default IdleResources;
