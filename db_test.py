from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load .env
load_dotenv(dotenv_path=".env", override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL is:", DATABASE_URL)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT current_user, current_database()")).fetchone()
    print("Connected as:", result[0])
    print("Database:", result[1])
