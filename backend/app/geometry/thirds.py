"""
Facial Thirds Analysis
========================
Analyzes vertical facial proportions by dividing the face into three zones:

  Upper third:  Hairline → Eyebrows
  Middle third: Eyebrows → Base of Nose
  Lower third:  Base of Nose → Chin

Calculates proportions and scores based on deviation from a
configurable reference distribution (default: equal thirds).

The reference distribution is NOT claimed to be universally ideal.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.cv.landmark_detector import FaceLandmarks, LANDMARK_INDICES
from app.geometry.utils import vertical_distance, clamp


@dataclass
class FacialThirdsResult:
    """Facial thirds analysis result."""
    upper_third: float = 0.0   # Proportion (0-1)
    middle_third: float = 0.0  # Proportion (0-1)
    lower_third: float = 0.0   # Proportion (0-1)
    score: float = 0.0         # Deviation score (0-100)


def analyze_facial_thirds(landmarks: FaceLandmarks) -> FacialThirdsResult:
    """
    Analyze vertical facial thirds.

    Landmark mapping:
    - Hairline → forehead_top (index 10)
    - Eyebrow line → average of left/right eyebrow bottom points
    - Nose base → nose_bottom (index 2)
    - Chin → chin (index 152)

    Args:
        landmarks: Extracted facial landmarks.

    Returns:
        FacialThirdsResult with proportions and score.
    """
    # Key vertical landmarks
    hairline = landmarks.get_landmark("forehead_top")
    chin = landmarks.get_landmark("chin")
    nose_base = landmarks.get_landmark("nose_bottom")

    # Eyebrow line: average y-coordinate of the lowest eyebrow points
    left_brow_points = landmarks.get_region("left_eyebrow")
    right_brow_points = landmarks.get_region("right_eyebrow")
    all_brow_points = left_brow_points + right_brow_points

    # Use the bottom (highest y) of the eyebrows as the dividing line
    brow_y = max(p.y for p in all_brow_points)
    from app.cv.landmark_detector import Point2D
    eyebrow_line = Point2D(x=0.5, y=brow_y)

    # Total face height
    total_height = vertical_distance(hairline, chin)
    if total_height < 1e-10:
        return FacialThirdsResult()

    # Three segments
    upper = vertical_distance(hairline, eyebrow_line)
    middle = vertical_distance(eyebrow_line, nose_base)
    lower = vertical_distance(nose_base, chin)

    # Proportions
    upper_prop = upper / total_height
    middle_prop = middle / total_height
    lower_prop = lower / total_height

    # Score: deviation from reference distribution
    ref = settings.facial_thirds
    deviations = [
        abs(upper_prop - ref.reference_upper),
        abs(middle_prop - ref.reference_middle),
        abs(lower_prop - ref.reference_lower),
    ]
    mean_deviation = sum(deviations) / len(deviations)

    # Convert deviation to score
    # A mean deviation of 0 → 100, deviation of 0.1 → ~67
    score = clamp(100.0 * (1.0 - mean_deviation * 3.0))

    return FacialThirdsResult(
        upper_third=round(upper_prop, 3),
        middle_third=round(middle_prop, 3),
        lower_third=round(lower_prop, 3),
        score=round(score, 1),
    )
