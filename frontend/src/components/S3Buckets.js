// src/components/S3Buckets.js
import React, { useEffect, useState } from "react";
import axios from "../api";
import { Table, Spinner, Alert } from "react-bootstrap";

const S3Buckets = ({ provider }) => {
  const [buckets, setBuckets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBuckets = async () => {
      try {
        setLoading(true);
        const res = await axios.get("/storage", { params: { provider } });
        setBuckets(res.data.buckets || []);
      } catch (err) {
        console.error("Error fetching buckets:", err);
        setError("Failed to load buckets.");
      } finally {
        setLoading(false);
      }
    };
    fetchBuckets();
  }, [provider]);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (buckets.length === 0)
    return <Alert variant="info">No storage buckets found.</Alert>;

  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>Name</th>
          <th>Creation Date</th>
          <th>Public?</th>
        </tr>
      </thead>
      <tbody>
        {buckets.map((b) => (
          <tr key={b.name}>
            <td>{b.name}</td>
            <td>{b.creation_date}</td>
            <td>{b.public_access ? "Yes" : "No"}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default S3Buckets;
