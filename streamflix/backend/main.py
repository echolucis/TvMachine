"""
StreamFlix Backend API

An open-source IPTV and Plex alternative for streaming movies, TV shows, and live TV.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from models import init_db
from api.routes import content, auth, iptv, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    print(f"🎬 StreamFlix API started on http://{settings.host}:{settings.port}")
    yield
    # Shutdown
    print("👋 StreamFlix API shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="Open-source IPTV and Plex alternative - Stream movies, TV shows, and live TV",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(iptv.router, prefix="/api/v1/iptv", tags=["IPTV"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Open-source IPTV and Plex alternative",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }
