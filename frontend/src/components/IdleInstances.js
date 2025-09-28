// src/components/IdleInstances.js
import React, { useEffect, useState } from "react";
import axios from "../api";
import { Table, Spinner, Alert } from "react-bootstrap";

const IdleInstances = () => {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchIdle = async () => {
      try {
        setLoading(true);
        const res = await axios.get("/resources/idle");
        setResources(res.data.idle_resources || []);
      } catch (err) {
        console.error("Error fetching idle resources:", err);
        setError("Failed to load idle resources.");
      } finally {
        setLoading(false);
      }
    };

    fetchIdle();
  }, []);

  if (loading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{error}</Alert>;
  if (resources.length === 0)
    return <Alert variant="info">No idle resources detected.</Alert>;

  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>ID</th>
          <th>Type</th>
          <th>Status</th>
          <th>Launch Time</th>
          <th>Est. Cost</th>
        </tr>
      </thead>
      <tbody>
        {resources.map((res) => (
          <tr key={res.id}>
            <td>{res.id}</td>
            <td>{res.type}</td>
            <td>{res.state}</td>
            <td>{res.launch_time}</td>
            <td>${res.estimated_cost}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default IdleInstances;
