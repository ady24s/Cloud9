import React, { useEffect, useState } from "react";
import { Table, Spinner, Alert } from "react-bootstrap";
import axios from "axios";

const S3Buckets = () => {
  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getBuckets = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/aws/s3");
        console.log("Fetched Buckets: ", response.data); // Debugging Line

        if (response.data && response.data.buckets) {
          setBuckets(response.data.buckets);
        } else {
          setError("Invalid data structure received from API");
        }
      } catch (err) {
        console.error("Error fetching S3 buckets:", err);
        setError("Failed to fetch S3 buckets");
      } finally {
        setLoading(false);
      }
    };

    getBuckets();
  }, []);

  return (
    <div>
      <h5>🪣 Active S3 Buckets</h5>
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
            {buckets.map((bucket) => (
              <tr key={bucket.name}>
                <td>{bucket.name}</td>
                <td>{bucket.creation_date}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default S3Buckets;
