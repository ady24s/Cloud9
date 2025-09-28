# schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

# -------- AUTH SCHEMAS --------
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str

class UserOut(BaseModel):
    id: int
    email: str
    provider: Optional[str]

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode


# -------- CLOUD CREDENTIALS --------
class CloudCredentialIn(BaseModel):
    provider: str
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    extra_json: Optional[str] = None

class CloudCredentialOut(BaseModel):
    id: int
    provider: str

    class Config:
        from_attributes = True


# -------- METRICS --------
class MetricOut(BaseModel):
    id: int
    provider: str
    vm_id: Optional[str]
    timestamp: Optional[str]
    cpu_usage: Optional[float]
    memory_usage: Optional[float]
    network_traffic: Optional[float]
    power_consumption: Optional[float]
    execution_time: Optional[float]
    task_type: Optional[str]

    class Config:
        from_attributes = True


# -------- METRIC INGESTION --------
class MetricIn(BaseModel):
    provider: str = Field(..., pattern="^(aws|azure|gcp)$")  # ✅ Pydantic v2 uses 'pattern'
    vm_id: str
    timestamp: str
    cpu_usage: Optional[float] = 0.0
    memory_usage: Optional[float] = 0.0
    network_traffic: Optional[float] = 0.0
    power_consumption: Optional[float] = 0.0
    execution_time: Optional[float] = 0.0
    task_type: Optional[str] = "general"

class MetricBatchIn(BaseModel):
    items: List[MetricIn]


# -------- INSIGHTS --------
class InsightOut(BaseModel):
    total_spend: float
    idle_resources: int
    predicted_savings: float
    anomalies: int
    avg_cpu: float
    avg_memory: float
    resources_observed: int


# -------- SPEND SERIES --------
class SpendPoint(BaseModel):
    date: str
    spend: float

class SpendSeries(BaseModel):
    points: List[SpendPoint]


# -------- OPTIMIZER --------
class OptimizerRecommendation(BaseModel):
    resource_id: str
    cluster_id: int
    recommendation: str

class OptimizerResponse(BaseModel):
    recommendations: List[OptimizerRecommendation]
