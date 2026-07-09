# =============================================================================
# AI-First CRM HCP Module - FastAPI Application
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Main FastAPI application entry point
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Main FastAPI application for the AI-First CRM HCP Module.

This application provides:
    - RESTful API for HCP management
    - RESTful API for Interaction logging and retrieval
    - RESTful API for Follow-up scheduling
    - AI-powered conversational interface via LangGraph
    - Integration with Groq LLM for intelligent processing

Tech Stack:
    - FastAPI (Python web framework)
    - SQLAlchemy (ORM)
    - PostgreSQL (Database)
    - LangGraph (AI Agent framework)
    - Groq LLM (Language model)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.hcp_routes import router as hcp_router
from app.api.interaction_routes import router as interaction_router
from app.api.follow_up_routes import router as follow_up_router
from app.api.agent_routes import router as agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database tables
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization warning: {e}")

    yield

    # Shutdown: Cleanup (if needed)
    print("Application shutting down.")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered Healthcare Professional CRM System",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "hcps": "/api/hcps",
            "interactions": "/api/interactions",
            "follow_ups": "/api/follow-ups",
            "agent_chat": "/api/agent/chat",
            "agent_tools": "/api/agent/tools",
        },
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


# Register API routers
app.include_router(hcp_router, prefix="/api")
app.include_router(interaction_router, prefix="/api")
app.include_router(follow_up_router, prefix="/api")
app.include_router(agent_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )