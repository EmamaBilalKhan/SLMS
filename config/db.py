from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = None
db = None

def connectdb():
    global client, db
    if client is None:
        try:
            client = MongoClient(os.environ.get("connectionString"))
            db = client.Cluster0
            print("MongoDB Connected")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

def get_db():
    global db
    if db is None:
        connectdb()
    return db