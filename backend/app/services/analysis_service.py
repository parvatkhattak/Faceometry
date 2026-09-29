"""
Analysis Service
=================
Orchestrates the full facial analysis pipeline:

  Image → Validation → Landmarks → Measurements →
  Symmetry → Golden Ratio → Thirds → Fifths →
  Scoring → Response

This service is the single entry point for the API layer.
It coordinates all CV, geometry, and scoring modules.
"""

from __future__ import annotations

import logging
from typing import Optional

import cv2
import numpy as np

from app.cv.image_validator import ImageValidator, ValidationResult
from app.cv.landmark_detector import LandmarkDetector, FaceLandmarks
from app.cv.visualizer import draw_landmarks, encode_image_to_base64
from app.geometry.measurements import calculate_measurements, calculate_proportion_score
from app.geometry.symmetry import analyze_symmetry
from app.geometry.golden_ratio import analyze_golden_ratio
from app.geometry.thirds import analyze_facial_thirds
from app.geometry.fifths import analyze_facial_fifths
from app.scoring.engine import calculate_harmony_score
from app.models.schemas import (
    AnalysisResponse,
    FaceInfo,
    PoseEstimate as PoseEstimateSchema,
    ScoreBreakdown,
    FacialMeasurements,
    GoldenRatioAnalysis,
    RatioAnalysis,
    SymmetryAnalysis,
    SymmetryDetail,
    FacialThirdsAnalysis,
    FacialFifthsAnalysis,
    ScoreExplanation as ScoreExplanationSchema,
)

logger = logging.getLogger(__name__)


class AnalysisService:
    """
    Main facial analysis service.

    Orchestrates the full pipeline from image bytes to structured
    analysis response. Handles all errors gracefully.

    Usage:
        service = AnalysisService()
        # Either validate + analyze, or use analyze_image for full pipeline
        result = service.analyze_image(image_bytes)
    """

    def __init__(self):
        self._detector = LandmarkDetector()
        self._validator = ImageValidator(detector=self._detector)

    def validate(self, image_bytes: bytes) -> ValidationResult:
        """
        Validate an image before analysis.

        Args:
            image_bytes: Raw image file bytes.

        Returns:
            ValidationResult with pass/fail and issues.
        """
        return self._validator.validate_from_bytes(image_bytes)

    def analyze_image(self, image_bytes: bytes) -> AnalysisResponse:
        """
        Run the full facial analysis pipeline.

        Pipeline:
          1. Decode image
          2. Validate (face detection, quality, pose)
          3. Extract landmarks
          4. Calculate measurements
          5. Analyze symmetry
          6. Analyze golden ratio proximity
          7. Analyze facial thirds
          8. Analyze facial fifths
          9. Calculate proportion score
          10. Calculate Facial Harmony Score
          11. Generate annotated image
          12. Build response

        Args:
            image_bytes: Raw image file bytes (JPEG, PNG, WebP).

        Returns:
            AnalysisResponse with all scores, measurements, and explanations.

        Raises:
            ValueError: If validation fails (caller should catch and return error).
        """
        # 1. Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image_bgr is None:
            raise ValueError("Failed to decode image. The file may be corrupt or in an unsupported format.")

        # 2. Validate
        validation = self._validator.validate(image_bgr)
        if not validation.is_valid:
            raise ValueError("; ".join(validation.issues))

        landmarks = validation.landmarks
        pose = validation.pose

        # 3-4. Calculate measurements
        measurements = calculate_measurements(landmarks)

        # 5. Symmetry analysis
        symmetry_result = analyze_symmetry(landmarks)

        # 6. Golden ratio analysis
        golden_result = analyze_golden_ratio(measurements)

        # 7. Facial thirds
        thirds_result = analyze_facial_thirds(landmarks)

        # 8. Facial fifths
        fifths_result = analyze_facial_fifths(landmarks)

        # 9. Proportion score
        proportion_score = calculate_proportion_score(measurements)

        # 10. Facial Harmony Score
        harmony = calculate_harmony_score(
            symmetry_score=symmetry_result.overall_score,
            proportion_score=proportion_score,
            golden_ratio_score=golden_result.overall_score,
            facial_thirds_score=thirds_result.score,
            facial_fifths_score=fifths_result.score,
        )

        # 11. Annotated landmark image
        annotated = draw_landmarks(image_bgr, landmarks)
        landmark_image_b64 = encode_image_to_base64(annotated)

        # 12. Build response
        return AnalysisResponse(
            success=True,
            face=FaceInfo(
                count=validation.face_count,
                pose=PoseEstimateSchema(
                    yaw=pose.yaw if pose else 0.0,
                    pitch=pose.pitch if pose else 0.0,
                    roll=pose.roll if pose else 0.0,
                ),
            ),
            scores=ScoreBreakdown(
                symmetry=harmony.symmetry_score,
                proportion=harmony.proportion_score,
                golden_ratio=harmony.golden_ratio_score,
                facial_thirds=harmony.facial_thirds_score,
                facial_fifths=harmony.facial_fifths_score,
                harmony=harmony.harmony_score,
            ),
            measurements=FacialMeasurements(**measurements.to_dict()),
            golden_ratio_analysis=GoldenRatioAnalysis(
                ratios=[
                    RatioAnalysis(
                        name=r.name,
                        value=r.value,
                        target=r.target,
                        deviation=r.deviation,
                        score=r.score,
                    )
                    for r in golden_result.ratios
                ],
                overall_score=golden_result.overall_score,
            ),
            symmetry_analysis=SymmetryAnalysis(
                overall_score=symmetry_result.overall_score,
                details=[
                    SymmetryDetail(
                        region=d.region,
                        error=round(d.error, 4),
                        score=round(d.score, 1),
                    )
                    for d in symmetry_result.details
                ],
            ),
            facial_thirds=FacialThirdsAnalysis(
                upper_third=thirds_result.upper_third,
                middle_third=thirds_result.middle_third,
                lower_third=thirds_result.lower_third,
                score=thirds_result.score,
            ),
            facial_fifths=FacialFifthsAnalysis(
                sections=fifths_result.sections,
                score=fifths_result.score,
            ),
            explanations=[
                ScoreExplanationSchema(
                    component=e.component,
                    score=e.score,
                    explanation=e.explanation,
                )
                for e in harmony.explanations
            ],
            landmark_image_base64=landmark_image_b64,
        )
