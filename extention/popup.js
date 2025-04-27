async function fetchAlerts() {
    try {
        const metrics = await fetch("http://127.0.0.1:8000/metrics").then(res => res.json());
        const security = await fetch("http://127.0.0.1:8000/security").then(res => res.json());

        document.getElementById("budgetStatus").textContent = metrics.totalSpend > 25000 ? "⚠️ Over Budget" : "✅ OK";
        document.getElementById("idleResources").textContent = metrics.idleResources + " detected";
        document.getElementById("securityIssues").textContent = security.issues_found + " issues";

    } catch (error) {
        console.error("Error fetching alerts:", error);
        document.getElementById("alerts").innerHTML = "<p>❌ Error fetching data.</p>";
    }
}

fetchAlerts();
