import React, { useEffect, useState } from "react";
import { Table, Spinner, Alert } from "react-bootstrap";
import axios from "axios";

const S3Buckets = ({ provider }) => {
  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getBuckets = async () => {
      try {
        let endpoint = "";

        if (provider === "aws") {
          endpoint = "http://127.0.0.1:8000/aws/s3";
        } else if (provider === "gcp") {
          endpoint = "http://127.0.0.1:8000/gcp/storage";
        } else if (provider === "azure") {
          endpoint = "http://127.0.0.1:8000/azure/storage";
        }

        const response = await axios.get(endpoint);

        console.log("Fetched Buckets: ", response.data);

        if (response.data && (response.data.buckets || Array.isArray(response.data))) {
          const data = response.data.buckets || response.data;

          setBuckets(data);
        } else {
          setError("Invalid data structure received from API");
        }
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
      <h5>🪣 Active Cloud Storage Buckets</h5>
      {loading && <Spinner animation="border" />}
      {error && <Alert variant="danger">{error}</Alert>}
      {!loading && !error && buckets.length === 0 && <p>No buckets found.</p>}
      {!loading && !error && buckets.length > 0 && (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>Name</th>
              <th>Creation Date</th>
            </tr>
          </thead>
          <tbody>
            {buckets.map((bucket, index) => (
              <tr key={index}>
                <td>{bucket.name}</td>
                <td>{bucket.creation_date || '2025-01-01'}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default S3Buckets;
