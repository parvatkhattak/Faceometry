"""
Analysis API Router
====================
POST /api/analyze — Accept an image, run the full facial analysis
pipeline, and return structured JSON results.

The image is processed in memory and deleted immediately after analysis.
No facial images are stored by default.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.config import settings
from app.models.schemas import AnalysisResponse, ErrorResponse, ValidationError
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])

# Singleton service instance
_service = AnalysisService()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type or corrupt image"},
        413: {"model": ErrorResponse, "description": "File too large"},
        422: {"model": ValidationError, "description": "Image validation failed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Analyze facial geometry",
    description=(
        "Upload a front-facing photograph to analyze facial proportions, "
        "symmetry, and geometric ratios. Returns a Facial Harmony Score "
        "with detailed breakdown and explanations."
    ),
)
async def analyze_face(
    image: UploadFile = File(..., description="Front-facing photograph (JPEG, PNG, or WebP)"),
) -> AnalysisResponse:
    """
    Analyze a facial photograph.

    Pipeline:
    1. Validate file type and size
    2. Read image bytes
    3. Run full analysis pipeline
    4. Return structured results
    5. Image bytes are garbage-collected (never stored)
    """
    # Validate file extension
    if image.filename:
        ext = Path(image.filename).suffix.lower()
        if ext not in settings.validation.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": f"Unsupported file type: {ext}. Allowed: {', '.join(settings.validation.allowed_extensions)}",
                },
            )

    # Validate content type
    allowed_content_types = [
        "image/jpeg", "image/png", "image/webp", "image/jpg",
    ]
    if image.content_type and image.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": f"Unsupported content type: {image.content_type}.",
            },
        )

    # Read image bytes
    try:
        image_bytes = await image.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(
            status_code=400,
            detail={"success": False, "error": "Failed to read uploaded file."},
        )
    finally:
        await image.close()

    # Check file size
    max_bytes = int(settings.validation.max_file_size_mb * 1024 * 1024)
    if len(image_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail={
                "success": False,
                "error": f"File too large ({len(image_bytes) / (1024*1024):.1f} MB). Maximum: {settings.validation.max_file_size_mb} MB.",
            },
        )

    # Run analysis
    try:
        result = _service.analyze_image(image_bytes)
        return result
    except ValueError as e:
        # Validation errors (no face, multiple faces, blur, pose, etc.)
        error_msg = str(e)
        issues = error_msg.split("; ") if "; " in error_msg else [error_msg]
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error": "Image validation failed",
                "issues": issues,
            },
        )
    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "An unexpected error occurred during analysis. Please try again.",
                "detail": str(e) if settings.debug else None,
            },
        )
