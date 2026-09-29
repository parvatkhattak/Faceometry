"""
Faceometry — FastAPI Application Entry Point
=============================================
AI-powered facial geometry and symmetry analysis platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.analyze import router as analyze_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered facial geometry and symmetry analysis platform. "
        "Uses computer vision, mathematical proportions, and machine learning "
        "to analyze facial structure and harmony."
    ),
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(analyze_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy"}
