import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Load .env variables
load_dotenv()

# Access MongoDB connection string from environment
MONGO_DETAILS = os.environ.get("MONGO_DETAILS")

client = MongoClient(MONGO_DETAILS)

# Connect to your specific DB
db = client.bookstoredb

def get_database() -> Database:
    return db
