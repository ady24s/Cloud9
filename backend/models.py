# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    provider = Column(String, nullable=True)       # "google" or "microsoft" or None
    provider_id = Column(String, unique=True, nullable=True)  # external id for SSO
    hashed_password = Column(String, nullable=True)  # for local users

    credentials = relationship("CloudCredential", back_populates="owner", cascade="all, delete-orphan")
    metrics = relationship("CloudMetric", back_populates="owner", cascade="all, delete-orphan")

class CloudCredential(Base):
    __tablename__ = "cloud_credentials"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # "aws" | "azure" | "gcp"
    access_key_enc = Column(Text, nullable=True)   # encrypted
    secret_key_enc = Column(Text, nullable=True)   # encrypted
    extra_json_enc = Column(Text, nullable=True)   # encrypted (GCP JSON or Azure secret)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="credentials")

class CloudMetric(Base):
    __tablename__ = "cloud_metrics"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=True)
    vm_id = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    cpu_usage = Column(Float, nullable=True)
    memory_usage = Column(Float, nullable=True)
    network_traffic = Column(Float, nullable=True)
    power_consumption = Column(Float, nullable=True)
    execution_time = Column(Float, nullable=True)
    task_type = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="metrics")
