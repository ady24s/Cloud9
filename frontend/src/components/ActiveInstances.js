import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, Spinner, Alert } from "react-bootstrap";

const ActiveInstances = ({ provider }) => {
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getInstances = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8010/instances?provider=${provider}`
        );
        setInstances(response.data.instances);
      } catch (err) {
        console.error("Error fetching instances:", err);
        setError("Failed to fetch instances");
      } finally {
        setLoading(false);
      }
    };

    getInstances();
  }, [provider]);

  return (
    <div>
      <h5>💻 Active Instances</h5>
      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}
      {!loading && !error && instances.length > 0 && (
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
                <th>Type</th>
                <th>State</th>
                <th>Launch Time</th>
              </tr>
            </thead>
            <tbody>
              {instances.map((instance) => (
                <tr key={instance.id}>
                  <td>{instance.id}</td>
                  <td>{instance.type}</td>
                  <td>{instance.state}</td>
                  <td>{instance.launch_time}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </div>
  );
};

export default ActiveInstances;
