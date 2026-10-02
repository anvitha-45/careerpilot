import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from server.config import settings

class DatabaseManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.is_connected = False
        # Embedded memory fallback for offline/development resilience
        self._local_store: Dict[str, List[Dict[str, Any]]] = {
            "profiles": [],
            "jobs": [],
            "applications": [],
            "interviews": [],
            "learning": []
        }
        self._local_storage_file = os.path.join(os.path.dirname(__file__), "..", "data", "local_db.json")

    async def initialize(self):
        """Initialize MongoDB connection with automatic fallback."""
        try:
            print(f"[Database] Connecting to MongoDB at {settings.MONGODB_URI}...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2500,
                connectTimeoutMS=2500
            )
            # Ping database to verify connection
            await self.client.admin.command('ping')
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_connected = True
            print(f"[Database] Successfully connected to MongoDB [{settings.MONGODB_DB_NAME}]")
            
            # Ensure indexes
            await self.db.jobs.create_index("id", unique=True)
            await self.db.applications.create_index("id", unique=True)
            await self.db.profiles.create_index("email")
        except Exception:
            print("[Database] Local MongoDB not detected. Running seamlessly on embedded document store.")
            self.is_connected = False
            self._load_local_storage()

    def _load_local_storage(self):
        try:
            if os.path.exists(self._local_storage_file):
                with open(self._local_storage_file, "r", encoding="utf-8") as f:
                    self._local_store = json.load(f)
        except Exception as err:
            print(f"[Database] Error reading local store: {err}")

    def _save_local_storage(self):
        try:
            os.makedirs(os.path.dirname(self._local_storage_file), exist_ok=True)
            with open(self._local_storage_file, "w", encoding="utf-8") as f:
                json.dump(self._local_store, f, indent=2, default=str)
        except Exception as err:
            print(f"[Database] Error saving local store: {err}")

    # Generic Collection Operations
    async def insert(self, collection_name: str, document: Dict[str, Any]) -> Dict[str, Any]:
        doc = dict(document)
        if "created_at" not in doc:
            doc["created_at"] = datetime.utcnow().isoformat()
        doc["updated_at"] = datetime.utcnow().isoformat()

        if self.is_connected and self.db is not None:
            col = self.db[collection_name]
            result = await col.insert_one(doc)
            doc["_id"] = str(result.inserted_id)
            return doc
        else:
            if collection_name not in self._local_store:
                self._local_store[collection_name] = []
            doc["_id"] = f"loc_{len(self._local_store[collection_name]) + 1}"
            self._local_store[collection_name].append(doc)
            self._save_local_storage()
            return doc

    async def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            col = self.db[collection_name]
            doc = await col.find_one(query)
            if doc and "_id" in doc:
                doc["_id"] = str(doc["_id"])
            return doc
        else:
            items = self._local_store.get(collection_name, [])
            for item in reversed(items):
                if all(item.get(k) == v for k, v in query.items()):
                    return dict(item)
            return None

    async def find(self, collection_name: str, query: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = query or {}
        if self.is_connected and self.db is not None:
            col = self.db[collection_name]
            cursor = col.find(query).limit(limit)
            results = []
            async for doc in cursor:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                results.append(doc)
            return results
        else:
            items = self._local_store.get(collection_name, [])
            results = []
            for item in reversed(items):
                if not query or all(item.get(k) == v for k, v in query.items()):
                    results.append(dict(item))
                if len(results) >= limit:
                    break
            return results

    async def update_one(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any], upsert: bool = False) -> bool:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        if self.is_connected and self.db is not None:
            col = self.db[collection_name]
            res = await col.update_one(query, {"$set": update_data}, upsert=upsert)
            return res.modified_count > 0 or (upsert and res.upserted_id is not None)
        else:
            items = self._local_store.get(collection_name, [])
            for item in items:
                if all(item.get(k) == v for k, v in query.items()):
                    item.update(update_data)
                    self._save_local_storage()
                    return True
            if upsert:
                new_doc = {**query, **update_data}
                await self.insert(collection_name, new_doc)
                return True
            return False

    async def delete_many(self, collection_name: str, query: Dict[str, Any]):
        if self.is_connected and self.db is not None:
            await self.db[collection_name].delete_many(query)
        else:
            if collection_name in self._local_store:
                self._local_store[collection_name] = [
                    item for item in self._local_store[collection_name]
                    if not all(item.get(k) == v for k, v in query.items())
                ]
                self._save_local_storage()

db = DatabaseManager()

