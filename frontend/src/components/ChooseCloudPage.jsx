import React from "react";

export default function ChooseCloudPage() {
  const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";

  const handleConnect = (provider) => {
    const token = localStorage.getItem("cloud9_token");

    if (!token) {
      // Handle missing/expired token
      alert("Session expired. Redirecting to login...");
      localStorage.removeItem("cloud9_token");
      window.location.href = "/";
      return;
    }

    // Attach token to backend request so Azure login knows who the user is
    window.location.href = `${apiUrl}/auth/${provider}/login?token=${encodeURIComponent(token)}`;
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h2>Connect Your Cloud Account</h2>
      <p>Choose your cloud provider to allow Cloud9 to monitor cost & usage.</p>

      <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem" }}>
        <button
          onClick={() => handleConnect("aws")}
          style={{
            flex: 1,
            background: "#FF9900",
            color: "white",
            padding: "1rem",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Connect AWS
        </button>

        <button
          onClick={() => handleConnect("gcp")}
          style={{
            flex: 1,
            background: "#EA4335",
            color: "white",
            padding: "1rem",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Connect GCP
        </button>

        <button
          onClick={() => handleConnect("azure")}
          style={{
            flex: 1,
            background: "#0078D4",
            color: "white",
            padding: "1rem",
            border: "none",
            borderRadius: "8px",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          Connect Azure
        </button>
      </div>

      <p style={{ marginTop: "2rem", fontSize: "0.9rem", color: "#555" }}>
        After connecting, we’ll securely store a refresh token to keep fetching
        your cost and usage data automatically. You can disconnect anytime from
        the settings page.
      </p>
    </div>
  );
}
