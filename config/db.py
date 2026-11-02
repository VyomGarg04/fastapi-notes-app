from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

DATABASES = {
    "development": "notes",
    "testing": "mindgrove_test",
    "production": "mindgrove_production",
}

if ENVIRONMENT not in DATABASES:
    raise ValueError(f"Invalid environment: {ENVIRONMENT}")

client = MongoClient(MONGO_URI)

db = client[DATABASES[ENVIRONMENT]]