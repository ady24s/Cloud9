import React, { useEffect, useState } from "react";
import { Table, Spinner, Alert } from "react-bootstrap";
import axios from "axios";

const ActiveInstances = ({ provider }) => {
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getInstances = async () => {
      try {
        let endpoint = "";

        // ✅ Dynamically decide API endpoint based on provider
        if (provider === "aws") {
          endpoint = "http://127.0.0.1:8000/aws/instances";
        } else if (provider === "gcp") {
          endpoint = "http://127.0.0.1:8000/gcp/instances";
        } else if (provider === "azure") {
          endpoint = "http://127.0.0.1:8000/azure/instances";
        }

        const response = await axios.get(endpoint);

        console.log("Fetched Instances: ", response.data); // Debugging Line

        if (response.data && (response.data.instances || Array.isArray(response.data))) {
          // AWS case (response.data.instances), or GCP/Azure (just array)
          const data = response.data.instances || response.data;

          setInstances(data);
        } else {
          setError("Invalid data structure received from API");
        }
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
      <h5>✅ Active Cloud Instances</h5>
      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}
      {!loading && !error && instances.length === 0 && <p>No instances found.</p>}
      {!loading && !error && instances.length > 0 && (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Type</th>
              <th>State</th>
            </tr>
          </thead>
          <tbody>
            {instances.map((instance, index) => (
              <tr key={index}>
                <td>{instance.id}</td>
                <td>{instance.type}</td>
                <td>{instance.state}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default ActiveInstances;
