from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sklearn.ensemble import IsolationForest
import smtplib
from email.mime.text import MIMEText
import random
from datetime import datetime, timedelta

# Initialize FastAPI app
app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./cloud_resources.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    resource_type = Column(String)
    status = Column(String)
    usage_hours = Column(Float)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models
class ResourceBase(BaseModel):
    name: str
    resource_type: str
    status: str
    usage_hours: float
    class Config:
        orm_mode = True

class ResourceUpdate(BaseModel):
    name: str | None = None
    resource_type: str | None = None
    status: str | None = None
    usage_hours: float | None = None

# -------------------- Core APIs --------------------

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI backend is running!"}

@app.get("/resources/")
def get_resources(db: Session = Depends(get_db)):
    return db.query(Resource).all()

@app.post("/resources/")
def create_resource(resource: ResourceBase, db: Session = Depends(get_db)):
    new_resource = Resource(**resource.dict())
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource

@app.put("/resources/{resource_id}")
def update_resource(resource_id: int, updated_resource: ResourceUpdate, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    for field, value in updated_resource.dict(exclude_unset=True).items():
        setattr(db_resource, field, value)
    db.commit()
    db.refresh(db_resource)
    return {"message": "Resource updated successfully", "resource": db_resource}

@app.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(db_resource)
    db.commit()
    return {"message": "Resource deleted successfully"}

# -------------------- Cloud Simulation --------------------

instance_types = {
    'aws': ["t2.micro", "m5.large", "c5.xlarge"],
    'gcp': ["n1-standard-1", "e2-medium", "n2-standard-2"],
    'azure': ["Standard_B1s", "Standard_D2s_v3", "Standard_F4s_v2"]
}
states = ["running", "stopped", "terminated"]

@app.get("/instances")
def get_instances(provider: str = Query("aws")):
    instances = []
    for _ in range(5):
        launch_time = datetime.now() - timedelta(days=random.randint(0, 300))
        instances.append({
            "id": f"{provider[:3]}-vm-{random.randint(1000, 9999)}",
            "type": random.choice(instance_types.get(provider, ["t2.micro"])),
            "state": random.choice(states),
            "launch_time": launch_time.strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_usage": round(random.uniform(1, 90), 2),
            "memory_usage": round(random.uniform(1, 85), 2),
            "uptime_hours": random.randint(10, 700),
            "network_in": random.randint(10, 3000),
            "disk_read": random.randint(10, 2000),
            "public_ip": random.choice([True, False]),
            "open_ports": random.sample([22, 80, 443, 3389], k=random.randint(0, 2))
        })
    return {"instances": instances}

@app.get("/storage")
def get_storage(provider: str = Query("aws")):
    buckets = []
    for _ in range(3):
        creation_date = datetime.now() - timedelta(days=random.randint(30, 900))
        buckets.append({
            "name": f"{provider[:3]}-storage-{random.randint(1000,9999)}",
            "creation_date": creation_date.strftime("%Y-%m-%d"),
            "public_access": random.choice([True, False])
        })
    return {"buckets": buckets}

@app.get("/security")
def get_security(provider: str = Query("aws")):
    """
    Simulate dynamic cybersecurity findings for Cloud9 Dashboard.
    """

    # Simulate Public Resource Exposure
    public_bucket_risk = random.choices([True, False], weights=[25, 75])[0]

    # Simulate Open Ports Risk
    high_risk_ports = [22, 3389, 80, 443]
    open_ports = random.sample(high_risk_ports, k=random.choice([0, 1, 2]))

    # Simulate IAM Misconfiguration
    iam_misconfig = random.choices([True, False], weights=[20, 80])[0]

    # Simulate Missing Encryption on Storage
    encryption_missing = random.choices([True, False], weights=[15, 85])[0]

    # Simulate MFA Enforcement Check
    mfa_missing = random.choices([True, False], weights=[10, 90])[0]

    # Simulate Compliance Score (Out of 100)
    compliance_score = random.randint(75, 99)
    if public_bucket_risk or open_ports or iam_misconfig:
        compliance_score -= random.randint(5, 15)
    if encryption_missing or mfa_missing:
        compliance_score -= random.randint(3, 10)
    compliance_score = max(50, compliance_score)

    # Simulate Threat Detection (e.g., suspicious IPs)
    suspicious_login = random.choices([True, False], weights=[10, 90])[0]

    # Build Recommendations List
    recommendations = []

    if public_bucket_risk:
        recommendations.append("Restrict public access to storage buckets.")
    if open_ports:
        recommendations.append("Close unnecessary ports (22/3389/80).")
    if iam_misconfig:
        recommendations.append("Review IAM policies and apply least privilege.")
    if encryption_missing:
        recommendations.append("Enable encryption on storage services.")
    if mfa_missing:
        recommendations.append("Enforce Multi-Factor Authentication (MFA) for all users.")
    if suspicious_login:
        recommendations.append("Investigate suspicious login attempts immediately.")

    if not recommendations:
        recommendations.append("No critical issues detected. Maintain current security posture.")

    return {
        "issues_found": len(recommendations) if recommendations else 0,
        "public_buckets": int(public_bucket_risk),
        "open_ports": open_ports,
        "iam_misconfiguration": bool(iam_misconfig),
        "encryption_missing": bool(encryption_missing),
        "mfa_missing": bool(mfa_missing),
        "suspicious_login_detected": bool(suspicious_login),
        "compliance_score": compliance_score,
        "recommendations": recommendations
    }


@app.get("/metrics")
def get_metrics():
    return {
        "totalSpend": random.randint(10000, 40000),
        "idleResources": random.randint(1, 5),
        "predictedSavings": random.randint(1000, 8000),
        "anomalies": random.randint(0, 3)
    }

@app.get("/spend-history")
def get_spend_history():
    return {
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "spend": [
            random.randint(1800, 2500),
            random.randint(2000, 2700),
            random.randint(2100, 2900),
            random.randint(2200, 3000),
            random.randint(2300, 3100),
            random.randint(4000, 5000)  # spike
        ]
    }

# -------------------- AI Idle Resource Detection --------------------

@app.get("/ai/idle-detection")
def detect_idle_resources(provider: str = Query("aws")):
    """
    Dynamically simulate cloud resources and detect idle ones using Isolation Forest AI.
    """
    # Simulate random resources
    resources = []
    for _ in range(15):  # 15 resources
        resources.append({
            "id": f"{provider[:3]}-res-{random.randint(1000, 9999)}",
            "resource_type": random.choice(["VM", "Storage", "Database"]),
            "cpu_usage": round(random.uniform(1, 90), 2),
            "memory_usage": round(random.uniform(1, 90), 2),
            "uptime": random.randint(10, 800),
            "network_in": random.randint(10, 5000),
            "disk_read": random.randint(5, 3000),
            "status": random.choice(["running", "stopped"])
        })

    df = pd.DataFrame(resources)

    # Apply Isolation Forest for anomaly (idle) detection
    model = IsolationForest(contamination=0.15, random_state=42)
    df["anomaly"] = model.fit_predict(df[["cpu_usage", "memory_usage", "uptime", "network_in", "disk_read"]])

    idle_resources = df[df["anomaly"] == -1].drop(columns=["anomaly"]).to_dict(orient="records")

    return {"idle_resources": idle_resources}

# -------------------- Email Alerts (Optional) --------------------

def send_email_alert(message):
    msg = MIMEText(message)
    msg["Subject"] = "Cloud Dashboard Alert"
    msg["From"] = "adyasha24@gmail.com"
    msg["To"] = "patilaarya106@gmail.com"
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("adyasha24@gmail.com", "xxxxx")
            server.sendmail(msg["From"], msg["To"], msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.get("/security/trend")
def get_security_trend():
    """
    Simulate compliance score trend over the past 7 days.
    """
    today = datetime.now()
    trend = []

    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        score = random.randint(75, 95)  # Simulate score
        trend.append({"date": day, "compliance_score": score})

    trend.reverse()  # Latest date last
    return trend

