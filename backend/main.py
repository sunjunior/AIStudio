"""AIStudio backend - FastAPI application."""

import os
import sys

_backend_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_backend_dir)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Set __package__ for relative imports when run directly
if __name__ == "__main__" and __package__ is None:
    __package__ = "backend"
    if _parent_dir not in sys.path:
        sys.path.insert(0, _parent_dir)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import init_db
from .routers import models_router, training_router, evaluation_router, publishing_router

app = FastAPI(
    title="AIStudio",
    description="AI Workflow Platform - Model Lifecycle Management",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(models_router)
app.include_router(training_router)
app.include_router(evaluation_router)
app.include_router(publishing_router)


@app.on_event("startup")
def on_startup():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    os.makedirs(config.HF_CACHE_DIR, exist_ok=True)
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


def main():
    uvicorn.run(
        "backend.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
        reload_excludes=["data/*"],
    )


if __name__ == "__main__":
    # Run from parent directory so "backend.main:app" resolves correctly
    import subprocess
    subprocess.run([
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", config.API_HOST,
        "--port", str(config.API_PORT),
        "--reload",
        "--reload-exclude", "data/*",
    ], cwd=_parent_dir)
