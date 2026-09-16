import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.config import settings
from server.database import db_manager
from server.seeds.seed_data import seed_initial_jobs

from server.routers.auth import router as auth_router
from server.routers.profile import router as profile_router
from server.routers.assessment import router as assessment_router
from server.routers.jobs import router as jobs_router
from server.routers.learning import router as learning_router
from server.routers.tailoring import router as tailoring_router
from server.routers.applications import router as applications_router
from server.routers.interview import router as interview_router
from server.routers.analytics import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed initial jobs if empty
    print(f"[{settings.PROJECT_NAME}] Initializing database and services...")
    db_manager.initialize()
    await seed_initial_jobs()
    print(f"[{settings.PROJECT_NAME}] Startup complete. Listening on {settings.HOST}:{settings.PORT}")
    yield
    # Shutdown
    print(f"[{settings.PROJECT_NAME}] Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic Job-Readiness & Application Copilot for Graduating Engineers",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local dev and custom ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(assessment_router)
app.include_router(jobs_router)
app.include_router(learning_router)
app.include_router(tailoring_router)
app.include_router(applications_router)
app.include_router(interview_router)
app.include_router(analytics_router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_mode": "MongoDB" if db_manager.is_mongo else "Embedded Local Document Store",
        "ai_provider": settings.AI_PROVIDER
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host=settings.HOST, port=settings.PORT, reload=True)

