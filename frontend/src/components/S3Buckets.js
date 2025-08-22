import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, Spinner, Alert } from "react-bootstrap";

const S3Buckets = ({ provider }) => {
  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getBuckets = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8010/storage?provider=${provider}`
        );
        setBuckets(response.data.buckets);
      } catch (err) {
        console.error("Error fetching buckets:", err);
        setError("Failed to fetch storage buckets");
      } finally {
        setLoading(false);
      }
    };

    getBuckets();
  }, [provider]);

  return (
    <div>
      <h5>🗄️ Storage Buckets</h5>
      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}
      {!loading && !error && buckets.length > 0 && (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>Name</th>
              <th>Creation Date</th>
              <th>Public Access</th>
            </tr>
          </thead>
          <tbody>
            {buckets.map((bucket) => (
              <tr key={bucket.name}>
                <td>{bucket.name}</td>
                <td>{bucket.creation_date}</td>
                <td>{bucket.public_access ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default S3Buckets;
