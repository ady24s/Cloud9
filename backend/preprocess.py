import pandas as pd
import os
from sqlalchemy import create_engine

# Filenames
RAW_CSV = "vmCloud_data.csv"
CLEANED_CSV = "cleaned_vm_data.csv"

# Check if cleaned CSV already exists
if os.path.exists(CLEANED_CSV):
    print("Found existing cleaned data. Loading from file...")
    df = pd.read_csv(CLEANED_CSV)
else:
    print("Cleaning raw dataset...")

    # Load raw dataset
    df = pd.read_csv(RAW_CSV)
    print("Columns:", df.columns)
    print("Original shape:", df.shape)

    # Step 1: Keep only required columns
    columns_to_keep = [
        "vm_id", "timestamp", "cpu_usage", "memory_usage", "network_traffic",
        "power_consumption", "execution_time", "task_type"
    ]
    df = df[columns_to_keep]

    # Step 2: Drop nulls
    df = df.dropna()

    # Step 3: Reduce rows for development (e.g., 100 rows)
    df = df.sample(n=100, random_state=42)

    # Step 4: Save cleaned dataset
    df.to_csv(CLEANED_CSV, index=False)
    print(f"Cleaned data saved to '{CLEANED_CSV}'")

print("Cleaned shape:", df.shape)
print(df.head())

# Connect to PostgreSQL
DB_USER = 'postgres'
DB_PASSWORD = '321root%40'  # <-- Replace with your actual password
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'cloud_data'    # <-- Replace with your DB name in pgAdmin

# Create SQLAlchemy engine
connection_string = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(connection_string)

# Push DataFrame to PostgreSQL
df.to_sql('cloud_metrics', engine, if_exists='replace', index=False)
print("Data inserted into PostgreSQL table 'cloud_metrics'")

