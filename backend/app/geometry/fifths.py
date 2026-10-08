"""
Facial Fifths Analysis
========================
Analyzes horizontal facial proportions by dividing the face into five zones:

  1. Left facial edge → Left eye outer corner
  2. Left eye outer corner → Left eye inner corner
  3. Left eye inner corner → Right eye inner corner (inter-eye region)
  4. Right eye inner corner → Right eye outer corner
  5. Right eye outer corner → Right facial edge

In classical analysis, these five sections are expected to be
approximately equal in width. The score measures deviation from
equal fifths.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.cv.landmark_detector import FaceLandmarks, LANDMARK_INDICES
from app.geometry.utils import horizontal_distance, clamp


@dataclass
class FacialFifthsResult:
    """Facial fifths analysis result."""
    sections: list[float] = field(default_factory=list)  # Five proportions (0-1)
    score: float = 0.0


def analyze_facial_fifths(landmarks: FaceLandmarks) -> FacialFifthsResult:
    """
    Analyze horizontal facial fifths.

    Divides the face horizontally into five sections and measures
    how close they are to equal widths.

    Args:
        landmarks: Extracted facial landmarks.

    Returns:
        FacialFifthsResult with proportions and score.
    """
    # Horizontal landmarks (left-to-right)
    face_left = landmarks.get_landmark("face_left")
    left_eye_outer = landmarks.get_point(LANDMARK_INDICES["left_eye_outer"])
    left_eye_inner = landmarks.get_point(LANDMARK_INDICES["left_eye_inner"])
    right_eye_inner = landmarks.get_point(LANDMARK_INDICES["right_eye_inner"])
    right_eye_outer = landmarks.get_point(LANDMARK_INDICES["right_eye_outer"])
    face_right = landmarks.get_landmark("face_right")

    # Total face width
    total_width = horizontal_distance(face_left, face_right)
    if total_width < 1e-10:
        return FacialFifthsResult(sections=[0.2] * 5, score=0.0)

    # Five sections (left-to-right)
    section_1 = horizontal_distance(face_left, left_eye_outer)     # Left face edge → left eye
    section_2 = horizontal_distance(left_eye_outer, left_eye_inner)  # Left eye width
    section_3 = horizontal_distance(left_eye_inner, right_eye_inner) # Inter-eye
    section_4 = horizontal_distance(right_eye_inner, right_eye_outer) # Right eye width
    section_5 = horizontal_distance(right_eye_outer, face_right)    # Right eye → right face edge

    # Proportions
    sections_raw = [section_1, section_2, section_3, section_4, section_5]
    sections = [s / total_width for s in sections_raw]

    # Score: deviation from equal fifths (each = 0.2)
    ideal = 0.2
    deviations = [abs(s - ideal) for s in sections]
    mean_deviation = sum(deviations) / len(deviations)

    # Convert deviation to score (sharper curve: dev 0.015 → 88, dev 0.035 → 72, dev 0.06 → 52)
    score = clamp(100.0 * (1.0 - mean_deviation * 8.0))

    return FacialFifthsResult(
        sections=[round(s, 3) for s in sections],
        score=round(score, 1),
    )
