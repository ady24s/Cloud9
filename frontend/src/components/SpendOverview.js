import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const SpendOverview = () => {
  const data = [
    { month: "Jan", spend: 2000 },
    { month: "Feb", spend: 2200 },
    { month: "Mar", spend: 2500 },
    { month: "Apr", spend: 2300 },
    { month: "May", spend: 2400 },
    { month: "Jun", spend: 2600 },
  ];

  return (
    <div>
      <h5 style={styles.title}>💰 Cloud Spend Overview</h5>
      <div style={{ height: 250 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="spend"
              stroke="#007bff"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const styles = {
  title: {
    marginBottom: "15px",
    fontWeight: "bold",
    color: "#333",
  },
};

export default SpendOverview;
