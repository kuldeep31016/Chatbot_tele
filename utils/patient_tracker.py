import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
import certifi
import pandas as pd

load_dotenv()  # Load .env file

class PatientTracker:
    def __init__(self):
        try:
            mongo_uri = os.getenv("MONGO_URI")
            dbname = os.getenv("MONGO_DB")

            if not mongo_uri or not dbname:
                raise ValueError("MongoDB credentials not fully set in environment variables")

            # ✅ Secure connection to MongoDB Atlas
            self.client = MongoClient(
                mongo_uri,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=30000
            )
            self.client.admin.command("ping")
            self.db = self.client[dbname]
            self.patients = self.db["patients"]
            self.consultations = self.db["consultations"]
            print("✅ Connected to MongoDB Atlas")

        except Exception as e:
            print(f"❌ Database not available. Patient tracking features will be limited. Error: {e}")
            self.client = None
            self.db = None
            self.patients = None
            self.consultations = None
