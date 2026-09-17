import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "euro24_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

if not API_KEY:
    raise ValueError("API_KEY must be set in .env")