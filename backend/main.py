from fastapi import FastAPI, Depends, HTTPException
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./cloud_resources.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models
class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    resource_type = Column(String)
    status = Column(String)
    usage_hours = Column(Float)

# Create database tables
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

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is running!"}

# CRUD Operations
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

# ------------------ Dummy AWS Data Generators ------------------
instance_types = ["t2.micro", "t2.small", "t2.medium", "t3.large", "m5.large"]
states = ["running", "stopped", "terminated"]

@app.get("/aws/instances")
def get_aws_instances():
    instances = []
    for _ in range(5):  # Generate 5 random instances
        launch_time = datetime.now() - timedelta(days=random.randint(0, 100))
        instances.append({
            "id": f"i-{random.randint(100000,999999)}fake",
            "type": random.choice(instance_types),
            "state": random.choice(states),
            "launch_time": launch_time.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return {"instances": instances}

@app.get("/aws/s3")
def get_s3_buckets():
    buckets = []
    for i in range(3):
        creation_date = datetime.now() - timedelta(days=random.randint(10, 365))
        buckets.append({
            "name": f"cloud9-bucket-{random.randint(1000,9999)}",
            "creation_date": creation_date.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return {"buckets": buckets}

# ------------------ AI Idle Detection ------------------
@app.get("/ai/idle-detection")
def detect_idle_resources():
    try:
        resources = pd.read_csv("resources.csv")
        features = resources[["cpu_usage", "memory_usage", "uptime", "network_in", "disk_read"]]
        model = IsolationForest(contamination=0.1, random_state=42)
        resources["anomaly"] = model.fit_predict(features)
        idle_resources = resources[resources["anomaly"] == -1].drop(columns=["anomaly"]).to_dict(orient="records")
        return {"idle_resources": idle_resources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in idle detection: {e}")

# ------------------ Static Metrics ------------------
@app.get("/metrics")
def get_metrics():
    return {
        "totalSpend": 12500,
        "idleResources": 5,
        "predictedSavings": 800,
        "anomalies": 3
    }

# ------------------ Email Alert (Placeholder) ------------------
def send_email_alert(message):
    msg = MIMEText(message)
    msg["Subject"] = "Cloud Dashboard Alert"
    msg["From"] = "youremail@example.com"
    msg["To"] = "recipient@example.com"
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("youremail@example.com", "yourpassword")
            server.sendmail(msg["From"], msg["To"], msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")


@app.get("/spend-history")
def get_spend_history():
    # Dummy 6-month spend history data
    return {
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "spend": [2000, 2200, 2500, 2300, 2400, 3100]  # last value is a spike
    }


@app.get("/gcp/instances")
def get_gcp_instances():
    return [
        {"id": "gcp-vm-001", "type": "n1-standard-1", "state": "RUNNING"},
        {"id": "gcp-vm-002", "type": "e2-medium", "state": "TERMINATED"},
        {"id": "gcp-vm-003", "type": "n2-standard-2", "state": "RUNNING"},
    ]
@app.get("/gcp/storage")
def get_gcp_storage_buckets():
    return [
        {"name": "gcp-bucket-001", "creation_date": "2024-11-01"},
        {"name": "gcp-bucket-002", "creation_date": "2025-01-12"},
    ]


@app.get("/azure/instances")
def get_azure_instances():
    return [
        {"id": "azure-vm-1", "type": "Standard_B1s", "state": "Running"},
        {"id": "azure-vm-2", "type": "Standard_D2s_v3", "state": "Stopped"}
    ]
@app.get("/azure/storage")
def get_azure_storage_buckets():
    return [
        {"name": "azure-container-001", "creation_date": "2024-10-15"},
        {"name": "azure-container-002", "creation_date": "2025-02-20"},
    ]
@app.get("/security")
def get_security_status():
    return {
        "issues_found": 1,
        "public_buckets": 1,
        "open_ports": [22, 8080],
        "recommendation": "Close unused ports and restrict public bucket access."
    }
