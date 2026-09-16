import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
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

# Serve Built React Frontend (Single-Port Unified Deployment)
client_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "dist"))
assets_dir = os.path.join(client_dist, "assets")

if os.path.exists(client_dist) and os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes or Swagger docs
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=404, detail="Not Found")
        target_file = os.path.join(client_dist, full_path)
        if os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(client_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host=settings.HOST, port=settings.PORT, reload=True)
