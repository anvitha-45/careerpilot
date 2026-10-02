import os
import json
from server.database import db

async def seed_initial_jobs():
    """Ensure database has initial sample job postings for testing and benchmarking."""
    try:
        existing = await db.find("jobs", limit=1)
        if not existing:
            sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_jds.json")
            if os.path.exists(sample_path):
                with open(sample_path, "r", encoding="utf-8") as f:
                    jobs = json.load(f)
                    for job in jobs:
                        await db.insert("jobs", job)
                print(f"[Seed] Successfully seeded {len(jobs)} initial job postings into database.")
            else:
                print(f"[Seed] Sample JDs file not found at {sample_path}")
        else:
            print("[Seed] Jobs collection already populated.")
    except Exception as e:
        print(f"[Seed] Exception during initial seeding: {e}")
