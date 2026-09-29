"""
Pydantic models for API requests and responses.
================================================
These models define the contract between backend and frontend.
The frontend should only depend on these structures, not on internal
calculation details.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PoseEstimate(BaseModel):
    """Estimated head pose angles in degrees."""
    yaw: float = Field(..., description="Left-right rotation in degrees")
    pitch: float = Field(..., description="Up-down rotation in degrees")
    roll: float = Field(..., description="Tilt rotation in degrees")


class FaceInfo(BaseModel):
    """Basic face detection information."""
    count: int = Field(..., description="Number of faces detected")
    pose: PoseEstimate = Field(..., description="Estimated head pose")


class ScoreBreakdown(BaseModel):
    """All component scores and the overall Facial Harmony Score."""
    symmetry: float = Field(..., ge=0, le=100, description="Symmetry score (0-100)")
    proportion: float = Field(..., ge=0, le=100, description="General proportion score (0-100)")
    golden_ratio: float = Field(..., ge=0, le=100, description="Golden ratio proximity score (0-100)")
    facial_thirds: float = Field(..., ge=0, le=100, description="Facial thirds score (0-100)")
    facial_fifths: float = Field(..., ge=0, le=100, description="Facial fifths score (0-100)")
    harmony: float = Field(..., ge=0, le=100, description="Overall Facial Harmony Score (0-100)")


class RatioAnalysis(BaseModel):
    """Single ratio compared to a target value (e.g., φ)."""
    name: str = Field(..., description="Human-readable ratio name")
    value: float = Field(..., description="Measured ratio value")
    target: float = Field(..., description="Target reference value")
    deviation: float = Field(..., description="Relative deviation from target")
    score: float = Field(..., ge=0, le=100, description="Proximity score (0-100)")


class GoldenRatioAnalysis(BaseModel):
    """Golden ratio analysis results."""
    ratios: list[RatioAnalysis] = Field(..., description="Per-ratio analysis")
    overall_score: float = Field(..., ge=0, le=100, description="Aggregate golden ratio score")


class SymmetryDetail(BaseModel):
    """Per-region symmetry detail."""
    region: str = Field(..., description="Facial region name")
    error: float = Field(..., description="Normalized symmetry error")
    score: float = Field(..., ge=0, le=100, description="Region symmetry score")


class SymmetryAnalysis(BaseModel):
    """Symmetry analysis results."""
    overall_score: float = Field(..., ge=0, le=100)
    details: list[SymmetryDetail] = Field(..., description="Per-region breakdown")


class FacialThirdsAnalysis(BaseModel):
    """Vertical facial thirds analysis."""
    upper_third: float = Field(..., description="Upper third proportion")
    middle_third: float = Field(..., description="Middle third proportion")
    lower_third: float = Field(..., description="Lower third proportion")
    score: float = Field(..., ge=0, le=100)


class FacialFifthsAnalysis(BaseModel):
    """Horizontal facial fifths analysis."""
    sections: list[float] = Field(..., description="Five section proportions left-to-right")
    score: float = Field(..., ge=0, le=100)


class FacialMeasurements(BaseModel):
    """All normalized facial measurements."""
    face_width: float = 0.0
    face_height: float = 0.0
    face_aspect_ratio: float = 0.0
    left_eye_width: float = 0.0
    right_eye_width: float = 0.0
    average_eye_width: float = 0.0
    inter_eye_distance: float = 0.0
    eye_face_width_ratio: float = 0.0
    nose_length: float = 0.0
    nose_width: float = 0.0
    nose_aspect_ratio: float = 0.0
    mouth_width: float = 0.0
    mouth_nose_ratio: float = 0.0
    hairline_to_nose_base: float = 0.0


class ScoreExplanation(BaseModel):
    """Human-readable explanation for a score component."""
    component: str
    score: float
    explanation: str


class AnalysisResponse(BaseModel):
    """Complete analysis response returned by POST /api/analyze."""
    success: bool = True
    face: FaceInfo
    scores: ScoreBreakdown
    measurements: FacialMeasurements
    golden_ratio_analysis: GoldenRatioAnalysis
    symmetry_analysis: SymmetryAnalysis
    facial_thirds: FacialThirdsAnalysis
    facial_fifths: FacialFifthsAnalysis
    explanations: list[ScoreExplanation] = Field(
        default_factory=list,
        description="Human-readable explanations for how scores were calculated.",
    )
    landmark_image_base64: str | None = Field(
        default=None,
        description="Base64-encoded annotated face image with landmarks overlay.",
    )


class ErrorResponse(BaseModel):
    """Structured error response."""
    success: bool = False
    error: str = Field(..., description="Human-readable error message")
    detail: str | None = Field(default=None, description="Technical detail for debugging")


class ValidationError(BaseModel):
    """Image validation error with specific issue details."""
    success: bool = False
    error: str = "Image validation failed"
    issues: list[str] = Field(..., description="List of validation issues found")
