import React, { useEffect, useState } from "react";
import { fetchAWSInstances } from "../services/api";

const AWSInstances = () => {
    const [instances, setInstances] = useState([]);

    useEffect(() => {
        const getInstances = async () => {
            const data = await fetchAWSInstances();
            setInstances(data);
        };

        getInstances();
    }, []);

    return (
        <div>
            <h2>AWS EC2 Instances</h2>
            <table border="1">
                <thead>
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
            </table>
        </div>
    );
};

export default AWSInstances;
