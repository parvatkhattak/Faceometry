"""
Symmetry Analysis Module
=========================
Analyzes bilateral facial symmetry by comparing corresponding
landmark positions across the facial midline.

For each bilateral landmark pair:
1. Estimate the facial midline from nose/chin landmarks.
2. Reflect left-side landmarks across the midline.
3. Calculate normalized Euclidean error: E_i = sqrt((x - x')^2 + (y - y')^2)
4. Aggregate errors into a symmetry score.

The score represents geometric symmetry, not any aesthetic judgment.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.cv.landmark_detector import FaceLandmarks, LANDMARK_INDICES, Point2D
from app.geometry.utils import (
    distance,
    normalize_distance,
    reflect_point_across_line,
    vertical_distance,
    clamp,
)


@dataclass
class RegionSymmetry:
    """Symmetry measurement for a single facial region."""
    region: str
    error: float  # Normalized mean error for this region
    score: float  # Score (0-100, higher = more symmetric)


@dataclass
class SymmetryResult:
    """Complete symmetry analysis result."""
    overall_score: float = 0.0
    details: list[RegionSymmetry] = field(default_factory=list)
    raw_errors: list[float] = field(default_factory=list)  # Per-landmark errors (for debugging)


# Bilateral landmark pairs: (left_indices, right_indices, region_name)
# "Left" = viewer's left (person's right), "Right" = viewer's right (person's left)
BILATERAL_PAIRS: list[tuple[list[int], list[int], str]] = [
    # Eyes
    (
        [33, 7, 163, 144, 145, 153, 154, 155, 133],     # Left eye
        [362, 382, 381, 380, 374, 373, 390, 249, 263],   # Right eye
        "eyes",
    ),
    # Eyebrows
    (
        [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],     # Left eyebrow
        [300, 293, 334, 296, 336, 285, 295, 282, 283, 276],  # Right eyebrow
        "eyebrows",
    ),
    # Nose sides
    (
        [129, 49, 131, 134, 51, 5],                      # Left nose
        [358, 279, 360, 363, 281, 5],                    # Right nose
        "nose",
    ),
    # Mouth corners
    (
        [61, 185, 40, 39, 37],                           # Left mouth
        [291, 409, 270, 269, 267],                       # Right mouth
        "mouth",
    ),
    # Jawline
    (
        [234, 127, 162, 21, 54, 103, 67, 109, 10],      # Left jaw
        [454, 356, 389, 251, 284, 332, 297, 338, 10],   # Right jaw
        "jawline",
    ),
    # Cheeks (selected contour points)
    (
        [93, 132, 58, 172, 136, 150, 149, 176, 148],    # Left cheek
        [323, 361, 288, 397, 365, 379, 378, 400, 377],  # Right cheek
        "cheeks",
    ),
]


def analyze_symmetry(landmarks: FaceLandmarks) -> SymmetryResult:
    """
    Analyze bilateral facial symmetry.

    Args:
        landmarks: Extracted facial landmarks.

    Returns:
        SymmetryResult with overall score and per-region breakdown.
    """
    # Estimate facial midline from forehead-to-chin landmarks
    midline_top = landmarks.get_landmark("forehead_top")
    midline_bottom = landmarks.get_landmark("chin")

    # Get face height for normalization
    face_height = vertical_distance(midline_top, midline_bottom)
    if face_height < 1e-10:
        return SymmetryResult(overall_score=0.0)

    region_results: list[RegionSymmetry] = []
    all_errors: list[float] = []

    for left_indices, right_indices, region_name in BILATERAL_PAIRS:
        # Ensure pairs are the same length
        pair_count = min(len(left_indices), len(right_indices))
        region_errors: list[float] = []

        for i in range(pair_count):
            left_pt = landmarks.get_point(left_indices[i])
            right_pt = landmarks.get_point(right_indices[i])

            # Reflect left point across the midline
            reflected = reflect_point_across_line(left_pt, midline_top, midline_bottom)

            # Error = distance between reflected left and actual right
            error = distance(reflected, right_pt)
            normalized_error = normalize_distance(error, face_height)

            region_errors.append(normalized_error)
            all_errors.append(normalized_error)

        if region_errors:
            mean_error = sum(region_errors) / len(region_errors)
            # Convert error to score: lower error = higher score
            # Scale factor: error of 0.05 (5% of face height) → score of ~50
            region_score = clamp(100.0 * (1.0 - mean_error * 10.0))
            region_results.append(
                RegionSymmetry(region=region_name, error=mean_error, score=region_score)
            )

    # Overall score: weighted average of region scores
    # Weight by number of landmarks in each region for fairness
    if region_results:
        total_score = sum(r.score for r in region_results)
        overall_score = total_score / len(region_results)
    else:
        overall_score = 0.0

    return SymmetryResult(
        overall_score=clamp(overall_score),
        details=region_results,
        raw_errors=all_errors,
    )
