import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio
from server.config import settings

class LocalCollection:
    """Async-compatible in-process JSON document store with MongoDB-like API."""
    def __init__(self, name: str, filepath: str):
        self.name = name
        self.filepath = filepath
        self._lock = asyncio.Lock()

    def _read_data(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get(self.name, [])
        except Exception:
            return []

    def _write_data(self, docs: List[Dict[str, Any]]):
        full_data = {}
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    full_data = json.load(f)
            except Exception:
                full_data = {}
        full_data[self.name] = docs
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(full_data, f, indent=2, default=str)

    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for k, v in query.items():
            if k == "$or":
                if not any(self._matches(doc, subq) for subq in v):
                    return False
                continue
            if isinstance(v, dict):
                # Simple operator support
                if "$in" in v and doc.get(k) not in v["$in"]:
                    return False
                if "$nin" in v and doc.get(k) in v["$nin"]:
                    return False
                if "$regex" in v:
                    import re
                    pattern = v["$regex"]
                    val = str(doc.get(k, ""))
                    flags = re.IGNORECASE if v.get("$options") == "i" else 0
                    if not re.search(pattern, val, flags):
                        return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    async def find(self, query: Optional[Dict[str, Any]] = None, sort: Optional[List] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        async with self._lock:
            docs = self._read_data()
            if query:
                docs = [d for d in docs if self._matches(d, query)]
            if sort:
                for key, direction in reversed(sort):
                    docs.sort(key=lambda x: x.get(key, 0) or 0, reverse=(direction == -1))
            if limit:
                docs = docs[:limit]
            return [dict(d) for d in docs]

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        async with self._lock:
            docs = self._read_data()
            for d in docs:
                if self._matches(d, query):
                    return dict(d)
            return None

    async def insert_one(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            docs = self._read_data()
            new_doc = dict(doc)
            if "_id" not in new_doc:
                new_doc["_id"] = str(uuid.uuid4())
            if "created_at" not in new_doc:
                new_doc["created_at"] = datetime.utcnow().isoformat()
            docs.append(new_doc)
            self._write_data(docs)
            return {"inserted_id": new_doc["_id"]}

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> Dict[str, Any]:
        async with self._lock:
            docs = self._read_data()
            matched = False
            for idx, d in enumerate(docs):
                if self._matches(d, query):
                    matched = True
                    if "$set" in update:
                        d.update(update["$set"])
                    else:
                        d.update(update)
                    d["updated_at"] = datetime.utcnow().isoformat()
                    docs[idx] = d
                    break
            if not matched and upsert:
                new_doc = dict(query)
                if "$set" in update:
                    new_doc.update(update["$set"])
                else:
                    new_doc.update(update)
                if "_id" not in new_doc:
                    new_doc["_id"] = str(uuid.uuid4())
                new_doc["created_at"] = datetime.utcnow().isoformat()
                docs.append(new_doc)
            self._write_data(docs)
            return {"matched_count": 1 if matched else 0, "upserted_id": new_doc.get("_id") if not matched and upsert else None}

    async def delete_one(self, query: Dict[str, Any]) -> Dict[str, Any]:
        async with self._lock:
            docs = self._read_data()
            initial_len = len(docs)
            docs = [d for d in docs if not self._matches(d, query)]
            self._write_data(docs)
            return {"deleted_count": initial_len - len(docs)}

    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        async with self._lock:
            docs = self._read_data()
            if not query:
                return len(docs)
            return len([d for d in docs if self._matches(d, query)])

class DatabaseManager:
    """Manages database connection with automatic fallback to embedded local store."""
    def __init__(self):
        self.is_mongo = False
        self.client = None
        self.db = None
        self._collections: Dict[str, Any] = {}
        self.store_filepath = os.path.join(settings.DATA_DIR, "careerpilot_store.json")

    def initialize(self):
        if settings.MONGODB_URI:
            try:
                from pymongo import MongoClient
                self.client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
                self.client.server_info()
                self.db = self.client[settings.MONGODB_DB_NAME]
                self.is_mongo = True
                print("Connected successfully to MongoDB.")
                return
            except Exception as e:
                print(f"MongoDB connection failed ({e}). Falling back to embedded local document store.")
        
        self.is_mongo = False
        print(f"Operating in Embedded Local Document Store mode: {self.store_filepath}")

    def get_collection(self, name: str):
        if self.is_mongo and self.db is not None:
            # Wrap PyMongo sync in async executor for transparent compatibility
            return AsyncMongoWrapper(self.db[name])
        
        if name not in self._collections:
            self._collections[name] = LocalCollection(name, self.store_filepath)
        return self._collections[name]

class AsyncMongoWrapper:
    def __init__(self, collection):
        self._col = collection

    async def find(self, query: Optional[Dict[str, Any]] = None, sort: Optional[List] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        def _exec():
            cursor = self._col.find(query or {})
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        return await loop.run_in_executor(None, _exec)

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._col.find_one(query))

    async def insert_one(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: self._col.insert_one(doc))
        return {"inserted_id": str(res.inserted_id)}

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: self._col.update_one(query, update, upsert=upsert))
        return {"matched_count": res.matched_count}

    async def delete_one(self, query: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: self._col.delete_one(query))
        return {"deleted_count": res.deleted_count}

    async def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self._col.count_documents(query or {}))

db_manager = DatabaseManager()
db_manager.initialize()

# Common collections
def get_users_col(): return db_manager.get_collection("users")
def get_profiles_col(): return db_manager.get_collection("profiles")
def get_jobs_col(): return db_manager.get_collection("jobs")
def get_matches_col(): return db_manager.get_collection("job_matches")
def get_skill_gaps_col(): return db_manager.get_collection("skill_gaps")
def get_learning_col(): return db_manager.get_collection("learning_plans")
def get_tailored_resumes_col(): return db_manager.get_collection("tailored_resumes")
def get_applications_col(): return db_manager.get_collection("applications")
def get_interviews_col(): return db_manager.get_collection("interview_sessions")

