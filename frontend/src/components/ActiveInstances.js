// src/components/ActiveInstances.js
import React, { useEffect, useState } from "react";
import axios from "../api";
import { Table, Spinner, Alert } from "react-bootstrap";


const ActiveInstances = ({ provider }) => {
  const [instances, setInstances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInstances = async () => {
      try {
        setLoading(true);
        const res = await axios.get("/instances", {
          params: { provider },
        });
        setInstances(res.data.instances || []);
      } catch (err) {
        console.error("Error fetching instances:", err);
        setError("Failed to load instances.");
      } finally {
        setLoading(false);
      }
    };

    if (provider) fetchInstances();
  }, [provider]);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (instances.length === 0)
    return <Alert variant="info">No active instances found.</Alert>;

  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>Instance ID</th>
          <th>Type</th>
          <th>Status</th>
          <th>Launch Time</th>
        </tr>
      </thead>
      <tbody>
        {instances.map((inst) => (
          <tr key={inst.id}>
            <td>{inst.id}</td>
            <td>{inst.type}</td>
            <td>{inst.state}</td>
            <td>{inst.launch_time}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default ActiveInstances;
