import pandas as pd

# Load dataset
df = pd.read_csv("vmCloud_data.csv")

# Preview columns
print("Columns:", df.columns)
print("Original shape:", df.shape)

# 1: Drop unnecessary columns (optional)
columns_to_keep = [
    "vm_id", "timestamp", "cpu_usage", "memory_usage", "network_traffic",
    "power_consumption", "execution_time", "task_type"
]
df = df[columns_to_keep]

# 2: Drop nulls
df = df.dropna()

# 3: Reduce size (e.g. keep only 5000 rows or filter certain task types)
df = df.sample(n=100, random_state=42)  # or use df[df['task_type'] == 'Computation']

# 4: Preview cleaned data
print("Cleaned shape:", df.shape)
print(df.head())

# 5: Save to cleaned file (optional)
df.to_csv("cleaned_vm_data.csv", index=False)
