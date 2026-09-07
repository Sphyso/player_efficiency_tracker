import os
from dotenv import load_dotenv

load_dotenv()

DATA_SOURCE = os.getenv("DATA_SOURCE", "offline")
API_KEY = os.getenv("API_KEY")

if DATA_SOURCE == "live" and not API_KEY:
    raise ValueError("DATA_SOURCE=live requires API_KEY to be set in .env")