import React, { useEffect, useState } from "react";
import { fetchIdleInstances } from "../services/api";

const IdleInstances = () => {
    const [idleInstances, setIdleInstances] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");

    useEffect(() => {
        const getIdleInstances = async () => {
            try {
                setLoading(true); // Start loading
                const data = await fetchIdleInstances();
                setIdleInstances(data); // Set the fetched data
            } catch (error) {
                console.error("Error fetching idle instances:", error);
            } finally {
                setLoading(false); // Stop loading
            }
        };

        getIdleInstances(); // Fetch data on component mount
    }, []);

    // Filter idle instances based on the search query
    const filteredInstances = idleInstances.filter(
        (instance) =>
            instance.id.toLowerCase().includes(search.toLowerCase()) ||
            instance.type.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="container my-4">
            <h2 className="text-center">Idle EC2 Instances</h2>

            {/* Search Input */}
            <input
                type="text"
                className="form-control mb-3"
                placeholder="Search by Instance ID or Type"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
            />

            {/* Loading Spinner */}
            {loading ? (
                <div className="text-center">
                    <div className="spinner-border" role="status">
                        <span className="sr-only">Loading...</span>
                    </div>
                </div>
            ) : filteredInstances.length === 0 ? (
                // No data found message
                <p className="text-center text-muted">No idle instances found.</p>
            ) : (
                // Display filtered data in a table
                <table className="table table-striped table-bordered">
                    <thead className="thead-dark">
                        <tr>
                            <th>Instance ID</th>
                            <th>Type</th>
                            <th>State</th>
                            <th>Launch Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredInstances.map((instance, index) => (
                            <tr key={index}>
                                <td>{instance.id}</td>
                                <td>{instance.type}</td>
                                <td>{instance.state}</td>
                                <td>{instance.launch_time}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default IdleInstances;
