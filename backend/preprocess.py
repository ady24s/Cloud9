# app/preprocess.py
import os
import pandas as pd
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from backend.database import engine, SessionLocal
from backend.models import Base, CloudMetric

# Load environment variables
load_dotenv(dotenv_path="../.env", override=True)

# File paths
RAW_CSV = "vmCloud_data.csv"
CLEANED_CSV = "cleaned_vm_data.csv"

# Step 1: Ensure schema exists (safe if already created)
Base.metadata.create_all(bind=engine)

# Step 2: Load or clean dataset
if os.path.exists(CLEANED_CSV):
    print("📂 Found existing cleaned data. Loading from file...")
    df = pd.read_csv(CLEANED_CSV)
else:
    print("🧹 Cleaning raw dataset...")
    df = pd.read_csv(RAW_CSV)

    # Keep required columns only
    columns_to_keep = [
        "vm_id", "timestamp", "cpu_usage", "memory_usage", "network_traffic",
        "power_consumption", "execution_time", "task_type"
    ]
    df = df[columns_to_keep]

    # Drop rows with null values
    df = df.dropna()

    # Limit to 100 rows for dev mode
    df = df.sample(n=100, random_state=42)

    # Save cleaned version
    df.to_csv(CLEANED_CSV, index=False)
    print(f"✅ Cleaned data saved to '{CLEANED_CSV}'")

print("Cleaned dataset shape:", df.shape)
print(df.head())

# Step 3: Insert data into PostgreSQL via ORM
session: Session = SessionLocal()

try:
    # Optional: Clear old data (comment out if you want to append instead)
    session.query(CloudMetric).delete()
    session.commit()

    rows = []
    for _, r in df.iterrows():
        rows.append(CloudMetric(
            provider="aws",  # or "gcp"/"azure" if mixing providers
            vm_id=str(r["vm_id"]),
            timestamp=str(r["timestamp"]),
            cpu_usage=float(r["cpu_usage"]),
            memory_usage=float(r["memory_usage"]),
            network_traffic=float(r["network_traffic"]),
            power_consumption=float(r["power_consumption"]),
            execution_time=float(r["execution_time"]),
            task_type=str(r["task_type"]),
            user_id=None  # set to a real user ID later when user accounts exist
        ))

    session.bulk_save_objects(rows)
    session.commit()
    print(f"✅ Inserted {len(rows)} rows into 'cloud_metrics' table.")
except Exception as e:
    session.rollback()
    print(f"❌ Error inserting data: {e}")
finally:
    session.close()
