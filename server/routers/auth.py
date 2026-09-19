from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
import httpx
from jose import jwt
from server.models.user import UserCreate, UserLogin, Token, UserResponse, GoogleAuthRequest
from server.database import get_users_col, get_profiles_col
from server.routers.auth_deps import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate):
    users_col = get_users_col()
    existing_user = await users_col.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    user_doc = {
        "name": user_in.name,
        "email": user_in.email,
        "hashed_password": get_password_hash(user_in.password),
        "created_at": datetime.utcnow().isoformat()
    }
    result = await users_col.insert_one(user_doc)
    user_id = str(result["inserted_id"])

    # Initialize default candidate profile
    profiles_col = get_profiles_col()
    profile_doc = {
        "user_id": user_id,
        "full_name": user_in.name,
        "email": user_in.email,
        "phone": "+91 9876543210",
        "target_roles": ["Software Engineer", "Backend Developer"],
        "target_location": "India (Bengaluru, Hyderabad, Remote)",
        "work_mode": "Remote / Hybrid",
        "experience_years": 0.0,
        "education": "B.Tech in Computer Science & Engineering",
        "graduation_year": 2026,
        "github_username": "",
        "leetcode_username": "",
        "skill_vector": {
            "core_languages": ["Python", "Java"],
            "frameworks": ["FastAPI", "React"],
            "databases": ["SQL", "MongoDB"],
            "tools_devops": ["Git", "Docker"],
            "concepts": ["Data Structures", "Algorithms", "OOP"],
            "all_skills": ["Python", "Java", "FastAPI", "React", "SQL", "MongoDB", "Git", "Docker", "Data Structures", "Algorithms", "OOP"],
            "total_skills_count": 11,
            "experience_level": "Fresher"
        },
        "overall_readiness_score": 68,
        "created_at": datetime.utcnow().isoformat()
    }
    await profiles_col.insert_one(profile_doc)

    access_token = create_access_token(data={"sub": user_id, "email": user_in.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user_in.name,
            "email": user_in.email,
            "created_at": user_doc["created_at"]
        }
    }

@router.post("/login", response_model=Token)
async def login(login_in: UserLogin):
    users_col = get_users_col()
    user = await users_col.find_one({"email": login_in.email})
    if not user or not verify_password(login_in.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id, "email": user["email"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user["name"],
            "email": user["email"],
            "created_at": user.get("created_at")
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"],
        "avatar_url": current_user.get("avatar_url"),
        "created_at": current_user.get("created_at")
    }

@router.post("/google", response_model=Token)
async def google_auth(auth_in: GoogleAuthRequest):
    email = auth_in.email
    name = auth_in.name or "Google User"
    google_id = auth_in.google_id or ""
    avatar_url = auth_in.avatar_url or ""

    # If raw Google ID token (JWT) is provided, verify/decode it
    if auth_in.credential:
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"https://oauth2.googleapis.com/tokeninfo?id_token={auth_in.credential}",
                    timeout=5.0
                )
                if res.status_code == 200:
                    token_info = res.json()
                    email = token_info.get("email", email)
                    name = token_info.get("name", name)
                    google_id = token_info.get("sub", google_id)
                    avatar_url = token_info.get("picture", avatar_url)
        except Exception:
            # Fallback to local JWT claims extraction
            try:
                claims = jwt.get_unverified_claims(auth_in.credential)
                email = claims.get("email", email)
                name = claims.get("name", name)
                google_id = claims.get("sub", google_id)
                avatar_url = claims.get("picture", avatar_url)
            except Exception:
                pass

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication failed: Email address could not be verified."
        )

    users_col = get_users_col()
    user = await users_col.find_one({"email": email})

    if not user:
        user_doc = {
            "name": name,
            "email": email,
            "google_id": google_id,
            "avatar_url": avatar_url,
            "auth_provider": "google",
            "hashed_password": "",
            "created_at": datetime.utcnow().isoformat()
        }
        result = await users_col.insert_one(user_doc)
        user_id = str(result["inserted_id"])

        # Auto-scaffold candidate profile for new Google user
        profiles_col = get_profiles_col()
        profile_doc = {
            "user_id": user_id,
            "full_name": name,
            "email": email,
            "phone": "+91 9876543210",
            "avatar_url": avatar_url,
            "target_roles": ["Software Engineer", "Backend Developer"],
            "target_location": "India (Bengaluru, Hyderabad, Remote)",
            "work_mode": "Remote / Hybrid",
            "experience_years": 0.0,
            "education": "B.Tech in Computer Science & Engineering",
            "graduation_year": 2026,
            "github_username": "",
            "leetcode_username": "",
            "skill_vector": {
                "core_languages": ["Python", "Java"],
                "frameworks": ["FastAPI", "React"],
                "databases": ["SQL", "MongoDB"],
                "tools_devops": ["Git", "Docker"],
                "concepts": ["Data Structures", "Algorithms", "OOP"],
                "all_skills": ["Python", "Java", "FastAPI", "React", "SQL", "MongoDB", "Git", "Docker", "Data Structures", "Algorithms", "OOP"],
                "total_skills_count": 11,
                "experience_level": "Fresher"
            },
            "overall_readiness_score": 68,
            "created_at": datetime.utcnow().isoformat()
        }
        await profiles_col.insert_one(profile_doc)
    else:
        user_id = str(user["_id"])
        # Update google attributes if new
        update_fields = {}
        if google_id and not user.get("google_id"):
            update_fields["google_id"] = google_id
        if avatar_url and not user.get("avatar_url"):
            update_fields["avatar_url"] = avatar_url
        if update_fields:
            await users_col.update_one({"_id": user["_id"]}, {"$set": update_fields})

    access_token = create_access_token(data={"sub": user_id, "email": email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user.get("name", name) if user else name,
            "email": email,
            "avatar_url": avatar_url or (user.get("avatar_url") if user else ""),
            "created_at": user.get("created_at") if user else user_doc["created_at"]
        }
    }


