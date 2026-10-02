import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from server.config import settings
from server.database import db
from server.seeds.seed_data import seed_initial_jobs
from server.routers.api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[{settings.PROJECT_NAME}] Starting up CareerPilot Agentic Pipeline v{settings.VERSION}...")
    await db.initialize()
    await seed_initial_jobs()
    print(f"[{settings.PROJECT_NAME}] Initialization complete. Copilot ready.")
    yield
    print(f"[{settings.PROJECT_NAME}] Shutting down...")
    if db.client:
        db.client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic Job-Readiness & Application Copilot for Graduating Engineers",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)

# Serve Web Dashboard
template_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates", "index.html"))

@app.get("/")
async def serve_home():
    if os.path.exists(template_file):
        return FileResponse(template_file)
    raise HTTPException(status_code=404, detail="Dashboard template not found")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Pass through API requests
    if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
        raise HTTPException(status_code=404, detail="Not Found")
    if os.path.exists(template_file):
        return FileResponse(template_file)
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host=settings.HOST, port=settings.PORT, reload=True)
