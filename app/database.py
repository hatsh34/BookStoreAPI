import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Load .env variables
load_dotenv()
# Access MongoDB connection string from environment
MONGO_DETAILS = os.environ.get("MONGO_DETAILS")

#Async client to connect to MongoDB instance.

client = AsyncIOMotorClient(MONGO_DETAILS)

#Motor uses dictionary-style access for databases.
db: AsyncIOMotorDatabase = client.bookstoredb

def get_database() -> AsyncIOMotorDatabase: 
    return db
    