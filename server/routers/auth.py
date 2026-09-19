from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from server.models.user import UserCreate, UserLogin, Token, UserResponse
from server.database import get_users_col, get_profiles_col
from server.routers.auth_deps import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate):
    users_col = get_users_col()
    username = user_in.username.strip().lower()

    # Verify username doesn't already exist
    check_query = [{"username": username}]
    if user_in.email:
        check_query.append({"email": user_in.email.strip().lower()})
    
    existing_user = await users_col.find_one({"$or": check_query})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username or email already exists."
        )

    user_name = user_in.name.strip() if user_in.name else username.capitalize()
    user_email = user_in.email.strip().lower() if user_in.email else f"{username}@careerpilot.local"

    user_doc = {
        "name": user_name,
        "username": username,
        "email": user_email,
        "hashed_password": get_password_hash(user_in.password),
        "created_at": datetime.utcnow().isoformat()
    }
    result = await users_col.insert_one(user_doc)
    user_id = str(result["inserted_id"])

    # Initialize default candidate profile
    profiles_col = get_profiles_col()
    profile_doc = {
        "user_id": user_id,
        "full_name": user_name,
        "username": username,
        "email": user_email,
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

    access_token = create_access_token(data={"sub": user_id, "username": username, "email": user_email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user_name,
            "username": username,
            "email": user_email,
            "created_at": user_doc["created_at"]
        }
    }

@router.post("/login", response_model=Token)
async def login(login_in: UserLogin):
    users_col = get_users_col()
    identifier = login_in.username.strip().lower()

    # Support login with either username or email
    user = await users_col.find_one({
        "$or": [
            {"username": identifier},
            {"email": identifier}
        ]
    })
    if not user or not verify_password(login_in.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = str(user["_id"])
    username = user.get("username", identifier)
    email = user.get("email", f"{username}@careerpilot.local")
    access_token = create_access_token(data={"sub": user_id, "username": username, "email": email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user.get("name", username.capitalize()),
            "username": username,
            "email": email,
            "created_at": user.get("created_at")
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user.get("name", "Candidate"),
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "created_at": current_user.get("created_at")
    }




