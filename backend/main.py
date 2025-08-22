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
from sklearn.model_selection import train_test_split

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
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:321root%40@127.0.0.1:5432/cloud_data"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CloudMetric(Base):
    __tablename__ = "cloud_metrics"

    vm_id = Column(String, primary_key=True)
    timestamp = Column(String)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    network_traffic = Column(Float)
    power_consumption = Column(Float)
    execution_time = Column(Float)
    task_type = Column(String)


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
    
class ChatMessage(BaseModel):
    message: str

# ----------- Core APIs ------------

@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

# ----------- Simulated Cloud APIs ------------

instance_types = {
    'aws': ["t2.micro", "m5.large", "c5.xlarge"],
    'gcp': ["n1-standard-1", "e2-medium", "n2-standard-2"],
    'azure': ["Standard_B1s", "Standard_D2s_v3", "Standard_F4s_v2"]
}
states = ["running", "stopped", "terminated"]

@app.get("/instances")
def get_instances(db: Session = Depends(get_db)):
    data = db.query(CloudMetric).limit(100).all()  # Fetch some rows for demo
    instances = []
    for row in data:
        instances.append({
            "id": row.vm_id,
            "type": random.choice(["t2.micro", "m5.large", "c5.xlarge"]),  
            "state": random.choice(["running", "stopped", "terminated"]),            
            "launch_time": row.timestamp,
        })
    return {"instances": instances}

# simulated data
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
def get_metrics(db: Session = Depends(get_db)):
    rows = db.query(CloudMetric).all()

    total_resources = len(rows)
    total_cpu = sum(r.cpu_usage for r in rows)
    total_memory = sum(r.memory_usage for r in rows)

    # Define idle resource as low CPU & Memory
    idle_count = sum(1 for r in rows if r.cpu_usage < 10 and r.memory_usage < 10)

    total_spend = round((total_cpu + total_memory) * 10, 2)  # Fake but real-derived
    predicted_savings = round(idle_count * 100, 2)
    anomalies = max(0, idle_count - 1)

    return {
        "totalSpend": total_spend,
        "idleResources": idle_count,
        "predictedSavings": predicted_savings,
        "anomalies": anomalies
    }
 
# simulated data   
@app.get("/spend-history")
def get_spend_history():
    return {
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "spend": [random.randint(1800, 3000) for _ in range(6)]
    }

# ----------- AI Idle Resource Detection ------------

@app.get("/ai/idle-detection")
def detect_idle_resources(db: Session = Depends(get_db)):
    rows = load_test_data(db)  # Use only test set
    resources = []
    for row in rows:
        resources.append({
            "id": row.vm_id,
            "cpu_usage": row.cpu_usage,
            "memory_usage": row.memory_usage,
            "uptime": row.execution_time,
            "network_in": row.network_traffic,
            "disk_read": row.power_consumption,
            "resource_type": "VM",
            "status": "Running"
        })

    df = pd.DataFrame(resources)
    if not df.empty:
        model = IsolationForest(contamination=0.15, random_state=42)
        df["anomaly"] = model.fit_predict(df[["cpu_usage", "memory_usage", "uptime", "network_in", "disk_read"]])

        for i in range(len(resources)):
            if df.loc[i, "anomaly"] == -1:
                resources[i]["status"] = "Idle"

    idle_resources = [res for res in resources if res["status"] == "Idle"]
    return {"idle_resources": idle_resources}  

# simulated data
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

# simulated data
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

def train_model():
    db = SessionLocal()
    try:
        rows = db.query(CloudMetric).all()
        resources = []
        for row in rows:
            resources.append([
                row.cpu_usage,
                row.memory_usage,
                row.execution_time,
                row.network_traffic,
                row.power_consumption
            ])

        if len(resources) < 3:
            print("Not enough data to train.")
            return

        features = np.array(resources)

        # Split into train/test
        X_train, X_test = train_test_split(features, test_size=0.2, random_state=42)

        # Save test set to disk for later predictions
        np.save("test_set.npy", X_test)

        # Train model
        scaler = StandardScaler()
        normalized_train = scaler.fit_transform(X_train)
        kmeans = KMeans(n_clusters=3, random_state=42)
        kmeans.fit(normalized_train)

        joblib.dump(kmeans, "kmeans_model.joblib")
        joblib.dump(scaler, "scaler.joblib")
        print("✅ Model and Scaler trained successfully on TRAIN set.")
    finally:
        db.close()
        
def load_test_data(db: Session):
    """Load test set rows from DB based on saved test_set.npy."""
    test_set = np.load("test_set.npy")
    # Fetch matching rows from DB (simple approach: just random sample for demo)
    all_rows = db.query(CloudMetric).all()
    return random.sample(all_rows, min(len(test_set), len(all_rows)))
    
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
                recommendation = "Downsize instance type"
            elif cluster_id == 1:
                recommendation = "Switch to spot instances"
            else:
                recommendation = "Archive idle storage"
            recommendations.append({
                "resource_id": resource["id"],
                "cluster_id": int(cluster_id),
                "recommendation": recommendation
            })
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in optimizer: {str(e)}")


@app.post("/optimizer")
def optimize_resources(db: Session = Depends(get_db)):
    rows = load_test_data(db)
    resources = []
    for row in rows:
        resources.append({
            "id": row.vm_id,
            "cpu_usage": row.cpu_usage,
            "memory_usage": row.memory_usage,
            "uptime": row.execution_time,
            "network_in": row.network_traffic,
            "disk_read": row.power_consumption
        })

    recommendations = run_optimizer(resources)
    return {"recommendations": recommendations}

@app.on_event("startup")
def startup_event():
    # Train model automatically when server starts
    if not (os.path.exists("kmeans_model.joblib") and os.path.exists("scaler.joblib") and os.path.exists("test_set.npy")):
        train_model()

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        return {"response": f"Message received: {message.message}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

