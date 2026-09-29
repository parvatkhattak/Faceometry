"""
Faceometry Configuration
========================
Central configuration using Pydantic Settings.
All thresholds, weights, and limits are defined here — not scattered throughout the codebase.
"""

from __future__ import annotations

import math
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


class ImageValidationSettings(BaseSettings):
    """Thresholds for image quality and pose validation."""

    # Face detection
    min_face_count: int = 1
    max_face_count: int = 1
    min_face_fraction: float = Field(
        default=0.10,
        description="Minimum fraction of image area the face bounding box must occupy.",
    )

    # Blur detection (Laplacian variance)
    blur_threshold: float = Field(
        default=50.0,
        description="Images with Laplacian variance below this are considered too blurry.",
    )

    # Lighting (mean pixel intensity)
    min_brightness: float = Field(default=40.0, description="Minimum mean brightness (0-255).")
    max_brightness: float = Field(default=220.0, description="Maximum mean brightness (0-255).")

    # Pose thresholds (degrees)
    max_yaw: float = Field(default=15.0, description="Maximum absolute yaw in degrees.")
    max_pitch: float = Field(default=15.0, description="Maximum absolute pitch in degrees.")
    max_roll: float = Field(default=10.0, description="Maximum absolute roll in degrees.")

    # Upload limits
    max_file_size_mb: float = 10.0
    allowed_extensions: list[str] = [".jpg", ".jpeg", ".png", ".webp"]

    model_config = ConfigDict(env_prefix="FACEOMETRY_VALIDATION_")


class ScoringSettings(BaseSettings):
    """Weights for the Facial Harmony Score components.

    These weights are EXPERIMENTAL and configurable.
    They are NOT scientifically validated as optimal.
    """

    weight_symmetry: float = Field(default=0.35, description="Symmetry weight (35%)")
    weight_proportion: float = Field(default=0.25, description="General proportion weight (25%)")
    weight_golden_ratio: float = Field(default=0.20, description="Golden ratio proximity weight (20%)")
    weight_facial_thirds: float = Field(default=0.10, description="Facial thirds weight (10%)")
    weight_facial_fifths: float = Field(default=0.10, description="Facial fifths weight (10%)")

    model_config = ConfigDict(env_prefix="FACEOMETRY_SCORING_")

    @property
    def weights(self) -> dict[str, float]:
        return {
            "symmetry": self.weight_symmetry,
            "proportion": self.weight_proportion,
            "golden_ratio": self.weight_golden_ratio,
            "facial_thirds": self.weight_facial_thirds,
            "facial_fifths": self.weight_facial_fifths,
        }


class GoldenRatioSettings(BaseSettings):
    """Configuration for which facial ratios are analyzed against φ.

    Only ratios explicitly listed here are compared to the golden ratio.
    Do NOT assume every facial measurement should ideally equal φ.
    """

    PHI: float = (1 + math.sqrt(5)) / 2  # ≈ 1.618033988749895

    # Ratios to analyze: list of (name, numerator_key, denominator_key)
    # These reference measurement keys from the geometry engine.
    analyzed_ratios: list[dict[str, str]] = [
        {"name": "Face Height / Face Width", "numerator": "face_height", "denominator": "face_width"},
        {"name": "Face Width / Inter-Eye Distance", "numerator": "face_width", "denominator": "inter_eye_distance"},
        {"name": "Nose Length / Nose Width", "numerator": "nose_length", "denominator": "nose_width"},
        {"name": "Mouth Width / Nose Width", "numerator": "mouth_width", "denominator": "nose_width"},
        {"name": "Face Height / Hairline-to-Nose", "numerator": "face_height", "denominator": "hairline_to_nose_base"},
    ]

    model_config = ConfigDict(env_prefix="FACEOMETRY_GOLDEN_")


class FacialThirdsSettings(BaseSettings):
    """Reference distribution for facial thirds.

    Default: equal thirds (1/3 each). This is a common classical reference,
    but it is NOT claimed to be universally ideal.
    """

    reference_upper: float = Field(default=1 / 3, description="Reference upper third proportion")
    reference_middle: float = Field(default=1 / 3, description="Reference middle third proportion")
    reference_lower: float = Field(default=1 / 3, description="Reference lower third proportion")

    model_config = ConfigDict(env_prefix="FACEOMETRY_THIRDS_")


class AppSettings(BaseSettings):
    """Top-level application settings."""

    app_name: str = "Faceometry"
    app_version: str = "1.0.0"
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Sub-settings
    validation: ImageValidationSettings = ImageValidationSettings()
    scoring: ScoringSettings = ScoringSettings()
    golden_ratio: GoldenRatioSettings = GoldenRatioSettings()
    facial_thirds: FacialThirdsSettings = FacialThirdsSettings()

    model_config = ConfigDict(env_prefix="FACEOMETRY_")


# Singleton instance
settings = AppSettings()
