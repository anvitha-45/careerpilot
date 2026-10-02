import os
import sys
import asyncio
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from httpx import AsyncClient, ASGITransport
from server.main import app
from server.database import db

async def run_auth_tests():
    print("[TEST] Initializing database...")
    await db.initialize()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Test registration
        test_username = f"testuser_{int(time.time() * 1000)}"
        test_email = f"{test_username}@example.com"
        print(f"[TEST] Registering new user: {test_username}")
        reg_res = await ac.post("/api/auth/register", json={
            "username": test_username,
            "password": "Password123!",
            "name": "Test Candidate",
            "email": test_email
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        data = reg_res.json()
        assert data["success"] is True
        assert data["user"]["username"] == test_username
        assert data["user"]["name"] == "Test Candidate"
        print("  [PASS] User registration successful")

        # 2. Test duplicate registration fails
        dup_res = await ac.post("/api/auth/register", json={
            "username": test_username,
            "password": "Password123!",
            "name": "Test Duplicate",
            "email": test_email
        })
        assert dup_res.status_code == 400
        assert "already exists" in dup_res.json()["detail"]
        print("  [PASS] Duplicate username prevented")

        # 3. Test successful login
        login_res = await ac.post("/api/auth/login", json={
            "username": test_username,
            "password": "Password123!"
        })
        assert login_res.status_code == 200
        assert login_res.json()["success"] is True
        assert login_res.json()["user"]["username"] == test_username
        print("  [PASS] User login successful")

        # 4. Test login with wrong password fails
        bad_login = await ac.post("/api/auth/login", json={
            "username": test_username,
            "password": "WrongPassword"
        })
        assert bad_login.status_code == 401
        print("  [PASS] Incorrect password rejected")

        # 5. Test guest attempting to save profile fails
        guest_save = await ac.post("/api/profile/save", json={
            "username": "Guest",
            "email": "guest@example.com",
            "name": "Guest User",
            "skills": ["Python"]
        })
        assert guest_save.status_code == 401
        assert "must log in" in guest_save.json()["detail"]
        print("  [PASS] Guest save blocked: login required")

        # 6. Test authenticated user saving profile succeeds
        auth_save = await ac.post("/api/profile/save", json={
            "username": test_username,
            "email": test_email,
            "name": "Test Candidate Updated",
            "phone": "+91 9988776655",
            "github_handle": "testcandidate",
            "leetcode_handle": "testcodes",
            "skills": ["Python", "FastAPI", "Docker"],
            "target_domain": "Backend"
        })
        assert auth_save.status_code == 200
        save_data = auth_save.json()
        assert save_data["success"] is True
        assert save_data["profile"]["name"] == "Test Candidate Updated"
        print("  [PASS] Logged in user saved profile successfully")

        # 7. Test retrieving saved profile
        get_prof = await ac.get(f"/api/profile?email={test_email}")
        assert get_prof.status_code == 200
        assert get_prof.json()["profile"]["username"] == test_username
        assert "FastAPI" in get_prof.json()["profile"]["skills"]
        print("  [PASS] Retrieved saved profile from database")

    print("\n[ALL AUTH & SAVE TESTS PASSED PERFECTLY!]\n")

if __name__ == "__main__":
    asyncio.run(run_auth_tests())
