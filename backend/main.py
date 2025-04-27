from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib

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

Base.metadata.create_all(bind=engine)

# Dependency

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

# ----------- Core APIs ------------

@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

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

# ----------- Simulated Cloud APIs ------------

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
        "spend": [random.randint(1800, 3000) for _ in range(6)]
    }

# ----------- AI Idle Resource Detection ------------

@app.get("/ai/idle-detection")
def detect_idle_resources(provider: str = Query("aws")):
    resources = []
    for _ in range(15):
        resources.append({
            "id": f"{provider[:3]}-res-{random.randint(1000, 9999)}",
            "resource_type": random.choice(["VM", "Storage", "Database"]),
            "cpu_usage": round(random.uniform(1, 90), 2),
            "memory_usage": round(random.uniform(1, 90), 2),
            "uptime": random.randint(10, 800),
            "network_in": random.randint(10, 5000),
            "disk_read": random.randint(5, 3000)
        })
    df = pd.DataFrame(resources)
    model = IsolationForest(contamination=0.15, random_state=42)
    df["anomaly"] = model.fit_predict(df[["cpu_usage", "memory_usage", "uptime", "network_in", "disk_read"]])
    idle_resources = df[df["anomaly"] == -1].drop(columns=["anomaly"]).to_dict(orient="records")
    return {"idle_resources": idle_resources}

@app.get("/security")
def get_security(provider: str = Query("aws")):
    """
    Simulate cybersecurity findings for Cloud9 Dashboard.
    """
    public_bucket_risk = random.choices([True, False], weights=[25, 75])[0]
    open_ports = random.sample([22, 3389, 80, 443], k=random.randint(0, 2))
    iam_misconfig = random.choices([True, False], weights=[20, 80])[0]
    encryption_missing = random.choices([True, False], weights=[15, 85])[0]
    mfa_missing = random.choices([True, False], weights=[10, 90])[0]
    suspicious_login = random.choices([True, False], weights=[10, 90])[0]

    compliance_score = random.randint(75, 99)
    if public_bucket_risk or open_ports or iam_misconfig:
        compliance_score -= random.randint(5, 15)
    if encryption_missing or mfa_missing:
        compliance_score -= random.randint(3, 10)
    compliance_score = max(50, compliance_score)

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
        recommendations.append("Enforce MFA for all users.")
    if suspicious_login:
        recommendations.append("Investigate suspicious login attempts immediately.")
    if not recommendations:
        recommendations.append("No critical issues detected.")

    return {
        "issues_found": len(recommendations),
        "public_buckets": int(public_bucket_risk),
        "open_ports": open_ports,
        "iam_misconfiguration": bool(iam_misconfig),
        "encryption_missing": bool(encryption_missing),
        "mfa_missing": bool(mfa_missing),
        "suspicious_login_detected": bool(suspicious_login),
        "compliance_score": compliance_score,
        "recommendations": recommendations
    }

@app.get("/security/trend")
def get_security_trend():
    """
    Simulate 7 days of compliance score trend.
    """
    today = datetime.now()
    trend = []
    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        score = random.randint(75, 95)
        trend.append({"date": day, "compliance_score": score})
    trend.reverse()
    return trend


def generate_fake_resources(n=10):
    resources = []
    for _ in range(n):
        resource_id = f"res-{random.randint(1000, 9999)}"
        resources.append({
            "id": resource_id,
            "cpu_usage": round(random.uniform(0, 90), 2),
            "memory_usage": round(random.uniform(0, 90), 2),
            "uptime": random.randint(0, 700),
            "network_in": random.randint(0, 5000),
            "disk_read": random.randint(0, 3000),
        })
    return resources
def train_model():
    """
    Trains a KMeans model with fake data and saves it to disk.
    """
    # Simulate training data
    fake_data = np.array([
        [5, 10, 100, 20, 50],    # underutilized
        [8, 15, 150, 30, 60],
        [50, 60, 300, 100, 200], # moderately utilized
        [55, 65, 350, 120, 220],
        [0, 0, 0, 5, 10],        # idle
        [0, 0, 0, 2, 5],
        [0, 0, 0, 3, 7],
    ])
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(fake_data)

    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(normalized_data)

    joblib.dump(kmeans, "kmeans_model.joblib")
    joblib.dump(scaler, "scaler.joblib")
    print("✅ Model and Scaler trained and saved successfully.")
def normalize_and_extract_features(resources):
    """
    Extract and normalize features from resource metrics.
    """
    features = []
    for resource in resources:
        features.append([
            resource.get("cpu_usage", 0),
            resource.get("memory_usage", 0),
            resource.get("uptime", 0),
            resource.get("network_in", 0),
            resource.get("disk_read", 0),
        ])
    return np.array(features)

def run_optimizer(resources):
    """
    Predict clusters and generate optimization recommendations.
    """
    try:
        kmeans = joblib.load("kmeans_model.joblib")
        scaler = joblib.load("scaler.joblib")

        features = normalize_and_extract_features(resources)
        normalized_features = scaler.transform(features)
        clusters = kmeans.predict(normalized_features)

        recommendations = []
        for i, resource in enumerate(resources):
            cluster_id = clusters[i]
            if cluster_id == 0:
                recommendation = "Downsize instance type (e.g., m5.large → t3.medium)"
            elif cluster_id == 1:
                recommendation = "Switch to spot instances"
            else:
                recommendation = "Archive idle S3 buckets to Glacier"

            recommendations.append({
                "resource_id": resource["id"],
                "cluster_id": int(cluster_id),
                "recommendation": recommendation
            })

        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in optimizer: {str(e)}")

@app.post("/optimizer")
def optimize_resources():
    resources = generate_fake_resources(12)
    recommendations = run_optimizer(resources)
    return {"recommendations": recommendations}

@app.on_event("startup")
def startup_event():
    # Train model automatically when server starts
    if not (os.path.exists("kmeans_model.joblib") and os.path.exists("scaler.joblib")):
        train_model()
