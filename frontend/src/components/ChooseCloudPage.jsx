// frontend/src/components/ChooseCloudPage.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ChooseCloudPage({ setCurrentProvider }) {  // ✅ Added prop
  const [selectedProvider, setSelectedProvider] = useState("");
  const [showCredentialForm, setShowCredentialForm] = useState(false);
  const [credentials, setCredentials] = useState({
    accessKey: "",
    secretKey: "", 
    extraJson: ""
  });
  const navigate = useNavigate();
  
  const apiUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";  // ✅ Added apiUrl

  const handleProviderSelect = (provider) => {
    setSelectedProvider(provider);
    setShowCredentialForm(true);
  };

  const handleConnect = async () => {
    const token = localStorage.getItem("cloud9_token");
    
    try {
      const response = await fetch(`${apiUrl}/credentials`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          provider: selectedProvider,
          access_key: credentials.accessKey,
          secret_key: credentials.secretKey,
          extra_json: credentials.extraJson || "{}"
        })
      });

      if (response.ok) {
        // Store the connected provider
        setCurrentProvider(selectedProvider); // ✅ This now works
        localStorage.setItem("current_provider", selectedProvider);
        alert(`${selectedProvider.toUpperCase()} connected successfully!`);
        navigate("/dashboard");
      }
    } catch (error) {
      console.error("Connection error:", error);
      alert("Connection failed");
    }
  };


  if (showCredentialForm) {
    return (
      <div style={{ padding: "2rem", maxWidth: "500px", margin: "auto" }}>
        <h2>Connect {selectedProvider.toUpperCase()} Account</h2>
        
        <div style={{ marginBottom: "1rem" }}>
          <label>Access Key / Client ID:</label>
          <input
            type="text"
            value={credentials.accessKey}
            onChange={(e) => setCredentials({...credentials, accessKey: e.target.value})}
            placeholder="AKIA... or client-id"
            style={{ width: "100%", padding: "0.5rem", marginTop: "0.5rem" }}
          />
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label>Secret Key / Client Secret:</label>
          <input
            type="password"
            value={credentials.secretKey}
            onChange={(e) => setCredentials({...credentials, secretKey: e.target.value})}
            placeholder="Your secret key"
            style={{ width: "100%", padding: "0.5rem", marginTop: "0.5rem" }}
          />
        </div>

        {(selectedProvider === "gcp" || selectedProvider === "azure") && (
          <div style={{ marginBottom: "1rem" }}>
            <label>Service Account JSON (GCP) / Tenant ID (Azure):</label>
            <textarea
              value={credentials.extraJson}
              onChange={(e) => setCredentials({...credentials, extraJson: e.target.value})}
              placeholder='{"project_id": "my-project"} or {"tenant_id": "..."}'
              rows="4"
              style={{ width: "100%", padding: "0.5rem", marginTop: "0.5rem" }}
            />
          </div>
        )}

        <button
          onClick={handleConnect}
          style={{
            background: "#007bff",
            color: "white",
            padding: "1rem 2rem",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            marginRight: "1rem"
          }}
        >
          Connect {selectedProvider.toUpperCase()}
        </button>

        <button
          onClick={() => setShowCredentialForm(false)}
          style={{
            background: "#6c757d",
            color: "white",
            padding: "1rem 2rem",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer"
          }}
        >
          Back
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h2>Connect Your Cloud Account</h2>
      <p>Choose your cloud provider and enter credentials to allow Cloud9 to monitor cost & usage.</p>

      <div style={{ display: "flex", gap: "1rem", marginTop: "1.5rem", flexDirection: "column" }}>
        <button
          onClick={() => handleProviderSelect("aws")}
          style={{
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
          onClick={() => handleProviderSelect("gcp")}
          style={{
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
          onClick={() => handleProviderSelect("azure")}
          style={{
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
    </div>
  );
}