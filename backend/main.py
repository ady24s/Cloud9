from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import os, numpy as np, pandas as pd, joblib
from apscheduler.schedulers.background import BackgroundScheduler

from backend.database import SessionLocal, engine
from backend.models import Base, CloudMetric
from backend import schemas
from backend.auth_deps import get_current_user_id
from backend.auth_router import router as auth_router
from backend.credentials_router import router as cred_router
from backend.cloud_ingestors import ingest_aws, ingest_gcp, ingest_azure

from datetime import timedelta
from sqlalchemy import text

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "super-secret-session-key")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

app = FastAPI(title="Cloud9 SaaS Backend")

# Session (Authlib needs this)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY, session_cookie="cloud9_session")

# CORS – restrict to your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_BASE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(cred_router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api")
def api_root():
    return {"message": "Cloud9 SaaS backend is running", "docs": "/docs", "status": "ok"}

# ---------------------- Metrics Ingestion ----------------------
@app.post("/metrics/ingest", response_model=int)
def ingest_metric(payload: schemas.MetricIn, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    row = CloudMetric(**payload.dict(), user_id=user_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row.id

@app.post("/metrics/ingest/batch", response_model=int)
def ingest_metric_batch(batch: schemas.MetricBatchIn, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = [CloudMetric(**item.dict(), user_id=user_id) for item in batch.items]
    db.bulk_save_objects(rows)
    db.commit()
    return len(rows)

# ---------------------- User Metrics & Insights ----------------------
@app.get("/users/me/metrics", response_model=List[schemas.MetricOut])
def my_metrics(limit: int = Query(200, ge=1, le=5000), db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return db.query(CloudMetric).filter(CloudMetric.user_id == user_id).order_by(CloudMetric.id.desc()).limit(limit).all()

@app.get("/users/me/insights", response_model=schemas.InsightOut)
def my_insights(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = db.query(CloudMetric).filter(CloudMetric.user_id == user_id).all()
    if not rows:
        return schemas.InsightOut(total_spend=0.0, idle_resources=0, predicted_savings=0.0, anomalies=0, avg_cpu=0.0, avg_memory=0.0, resources_observed=0)
    total_cpu = sum(r.cpu_usage or 0 for r in rows)
    total_mem = sum(r.memory_usage or 0 for r in rows)
    n = len(rows)
    idle = sum(1 for r in rows if (r.cpu_usage or 0) < 10 and (r.memory_usage or 0) < 10)
    return schemas.InsightOut(
        total_spend=round((total_cpu + total_mem) * 10, 2),
        idle_resources=idle,
        predicted_savings=round(idle * 100, 2),
        anomalies=max(0, idle - 1),
        avg_cpu=round(total_cpu / n, 2),
        avg_memory=round(total_mem / n, 2),
        resources_observed=n,
    )

@app.get("/users/me/spend-series", response_model=schemas.SpendSeries)
def my_spend_series(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = db.query(CloudMetric).filter(CloudMetric.user_id == user_id).all()
    cutoff = datetime.utcnow() - timedelta(days=days)
    buckets = {}
    for r in rows:
        try:
            ts = datetime.fromisoformat(r.timestamp.replace("Z", "")) if r.timestamp else datetime.utcnow()
        except:
            ts = datetime.utcnow()
        if ts >= cutoff:
            key = ts.strftime("%Y-%m-%d")
            buckets[key] = buckets.get(key, 0.0) + ((r.cpu_usage or 0) + (r.memory_usage or 0)) * 10.0
    pts = [schemas.SpendPoint(date=k, spend=round(v, 2)) for k, v in sorted(buckets.items())]
    return schemas.SpendSeries(points=pts)

# ---------------------- New Endpoints to Match Frontend ----------------------
@app.get("/instances")
def list_instances(provider: str, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = db.query(CloudMetric).filter(CloudMetric.user_id == user_id, CloudMetric.provider == provider).order_by(CloudMetric.id.desc()).limit(50).all()
    instances = [{"id": r.vm_id, "type": r.task_type or "unknown", "state": "running", "launch_time": r.timestamp} for r in rows]
    return {"status": "success", "instances": instances}

@app.get("/storage")
def list_storage(provider: str):
    # Mock response - later connect to real cloud storage APIs
    mock_buckets = [{"name": "project-data", "creation_date": "2025-09-01", "public_access": False},
                    {"name": "logs-archive", "creation_date": "2025-08-12", "public_access": True}]
    return {"status": "success", "buckets": mock_buckets}

@app.get("/users/me/security")
def security_overview():
    # Mock security posture
    data = {
        "compliance_score": 85,
        "public_buckets": True,
        "open_ports": ["22", "80"],
        "iam_misconfiguration": False,
        "encryption_missing": False,
        "mfa_missing": True,
        "suspicious_login_detected": False,
        "recommendations": [
            "Enable MFA for all users",
            "Restrict public S3 bucket access",
        ],
    }
    return {"status": "success", **data}

@app.get("/users/me/security/trend")
def security_trend():
    today = datetime.utcnow().date()
    points = [{"date": (today - timedelta(days=i)).isoformat(), "compliance_score": 80 + (i % 5)} for i in range(7)]
    return {"status": "success", "trend": points}

@app.get("/resources/idle")
def resources_idle(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = db.query(CloudMetric).filter(CloudMetric.user_id == user_id).order_by(CloudMetric.id.desc()).limit(50).all()
    idle = [{"id": r.vm_id, "type": r.task_type, "state": "running" if (r.cpu_usage or 0) > 5 else "idle",
             "launch_time": r.timestamp, "estimated_cost": round(((r.cpu_usage or 0) + (r.memory_usage or 0)) * 0.1, 2)}
            for r in rows]
    return {"status": "success", "idle_resources": idle}

@app.post("/chat")
async def chat_bot(req: Request):
    body = await req.json()
    question = body.get("question", "")
    answer = f"🤖 (Mock) You asked: '{question}'. Here is a placeholder response."
    return {"status": "success", "response": answer}

# ---------------------- AI & Optimizer (unchanged) ----------------------
@app.get("/users/me/ai/idle-detection")
def detect_idle(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = _load_eval_rows(db, user_id)
    if not rows:
        return {"idle_resources": []}
    resources = [{"id": r.vm_id, "resource_type": r.task_type or "vm", "cpu_usage": r.cpu_usage or 0.0,
                  "memory_usage": r.memory_usage or 0.0, "uptime": r.execution_time or 0.0,
                  "network_in": r.network_traffic or 0.0, "disk_read": r.power_consumption or 0.0,
                  "status": "Running"} for r in rows]
    df = pd.DataFrame(resources)
    from sklearn.ensemble import IsolationForest
    model = IsolationForest(contamination=0.15, random_state=42)
    df["anomaly"] = model.fit_predict(df[["cpu_usage", "memory_usage", "uptime", "network_in", "disk_read"]])
    for i in range(len(resources)):
        if df.loc[i, "anomaly"] == -1:
            resources[i]["status"] = "Idle"
    return {"status": "success", "idle_resources": [r for r in resources if r["status"] == "Idle"]}

@app.post("/users/me/optimizer", response_model=schemas.OptimizerResponse)
def optimize(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = _load_eval_rows(db, user_id)
    if not rows:
        return schemas.OptimizerResponse(recommendations=[])
    feats = np.array([[r.cpu_usage or 0.0, r.memory_usage or 0.0, r.execution_time or 0.0, r.network_traffic or 0.0, r.power_consumption or 0.0] for r in rows])
    kmeans, scaler = _get_or_train_user_model(db, user_id)
    Xn = scaler.transform(feats)
    clusters = kmeans.predict(Xn)
    recs = []
    for i, r in enumerate(rows):
        cid = int(clusters[i])
        msg = "Downsize instance type" if cid == 0 else "Switch to spot instances" if cid == 1 else "Archive idle storage"
        recs.append(schemas.OptimizerRecommendation(resource_id=r.vm_id or f"res-{r.id}", cluster_id=cid, recommendation=msg))
    return schemas.OptimizerResponse(recommendations=recs)

# ---------------------- ML Helpers ----------------------
def _user_dir(user_id: int):
    d = os.path.join("models", f"user_{user_id}")
    os.makedirs(d, exist_ok=True)
    return d

def _artifacts_exist(user_id: int):
    d = _user_dir(user_id)
    return all(os.path.exists(os.path.join(d, f)) for f in ["kmeans.joblib", "scaler.joblib"])

def _save_artifacts(user_id: int, kmeans, scaler):
    d = _user_dir(user_id)
    joblib.dump(kmeans, os.path.join(d, "kmeans.joblib"))
    joblib.dump(scaler, os.path.join(d, "scaler.joblib"))

def _load_artifacts(user_id: int):
    d = _user_dir(user_id)
    return joblib.load(os.path.join(d, "kmeans.joblib")), joblib.load(os.path.join(d, "scaler.joblib"))

def _get_or_train_user_model(db: Session, user_id: int):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    if _artifacts_exist(user_id):
        return _load_artifacts(user_id)
    rows = db.query(CloudMetric).filter(CloudMetric.user_id == user_id).all()
    feats = np.array([[r.cpu_usage or 0.0, r.memory_usage or 0.0, r.execution_time or 0.0, r.network_traffic or 0.0, r.power_consumption or 0.0] for r in rows]) or np.zeros((3, 5))
    scaler = StandardScaler().fit(feats)
    kmeans = KMeans(n_clusters=min(3, max(1, len(feats))), random_state=42).fit(scaler.transform(feats))
    _save_artifacts(user_id, kmeans, scaler)
    return kmeans, scaler

def _load_eval_rows(db: Session, user_id: int):
    return db.query(CloudMetric).filter(CloudMetric.user_id == user_id).order_by(CloudMetric.id.desc()).limit(200).all()

# ---------------------- Background Scheduler ----------------------
scheduler: Optional[BackgroundScheduler] = None

def _ingest_for_all_users():
    with SessionLocal() as db:
        user_ids = [uid for (uid,) in db.query(CloudMetric.user_id).distinct().all() if uid]
        cred_user_ids = [
    row[0]
    for row in db.execute(
        text("SELECT DISTINCT user_id FROM cloud_credentials WHERE user_id IS NOT NULL")
    )
]

        for uid in set(user_ids) | set(cred_user_ids):
            try:
                added = 0
                added += ingest_aws(db, uid)
                added += ingest_gcp(db, uid)
                added += ingest_azure(db, uid)
                if added:
                    _get_or_train_user_model(db, uid)
            except Exception as e:
                print(f"[ingest] user {uid} error: {e}")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    global scheduler
    scheduler = BackgroundScheduler(daemon=True, timezone="UTC")
    scheduler.add_job(_ingest_for_all_users, "interval", minutes=10, id="ingest", max_instances=1, coalesce=True)
    scheduler.start()
    print("⏱️ Multi-cloud ingestion running every 10 minutes.")

@app.on_event("shutdown")
def on_shutdown():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
    print("🛑 Scheduler shut down.")

# ---------------------- Serve React Frontend ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend_build")
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Frontend build not found"}
