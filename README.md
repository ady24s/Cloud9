# 🌩️ Cloud9 - AI Powered Cloud Optimization Dashboard

Cloud9 is an AI-driven cloud resource monitoring dashboard designed for startups and individuals to save cloud costs by detecting idle resources, predicting spend anomalies, and optimizing cloud utilization in real-time.

---

## 🚀 Features

- Intelligent Idle Resource Detection (Isolation Forest AI model)
- Dynamic AWS EC2 and S3 Monitoring (dummy simulation)
- Cloud Spend Overview Metrics
- Secure Email Alerts (optional SMTP support)
- Power BI Dashboard Embedding (for deeper analytics)
- Chrome Extension Style Frontend (ReactJS)
- Full Docker-based Containerization
- CI/CD with GitHub Actions

---

## 🛠 Tech Stack

- **Backend:** FastAPI, Python 3.10, Docker
- **Frontend:** ReactJS, Bootstrap, Axios
- **Database:** SQLite (lightweight for demo)
- **Machine Learning:** scikit-learn (Isolation Forest)
- **CI/CD:** GitHub Actions
- **Visualization:** Power BI (planned integration)

---

## ⚙️ Installation and Setup

1. Clone the Repository:

```bash
git clone https://github.com/ady24s/cloud9.git
cd cloud9




If you change backend code → auto reloads.

If you change frontend code → React hot reloads in browser.

If you change dependencies → just run docker compose build backend or docker compose exec frontend npm install.