"""
MongoDB Connection Singleton.
Provides shared db/collection handles used across the backend.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING

from backend.paths import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI not set in environment variables.")
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        _db = _client["ergonomics"]

        # Ensure indexes exist if connected
        try:
            _db["sessions"].create_index([("user_id", ASCENDING), ("started_at", DESCENDING)])
            _db["telemetry"].create_index([("session_id", ASCENDING), ("timestamp", ASCENDING)])
            _db["telemetry"].create_index([("user_id", ASCENDING)])
        except Exception as idx_err:
            print(f"[!] Warning: MongoDB index creation deferred or offline: {idx_err}")
    return _db


def users_col():
    return get_db()["users"]


def sessions_col():
    return get_db()["sessions"]


def telemetry_col():
    return get_db()["telemetry"]


def get_fs():
    import gridfs
    return gridfs.GridFS(get_db())
