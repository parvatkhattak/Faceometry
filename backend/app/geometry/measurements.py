"""
Facial Measurements Module
============================
Extracts all geometric measurements from facial landmarks.

All measurements are normalized by face height to make them
independent of image resolution and face size.

Measured features:
- Face: width, height, aspect ratio
- Eyes: width, inter-eye distance, eye-to-face ratio
- Nose: length, width, aspect ratio
- Mouth: width, mouth-to-nose ratio
"""

from __future__ import annotations

from dataclasses import dataclass

from app.cv.landmark_detector import FaceLandmarks, LANDMARK_INDICES
from app.geometry.utils import (
    distance,
    horizontal_distance,
    vertical_distance,
    midpoint,
    ratio,
    normalize_distance,
    clamp,
)


@dataclass
class MeasurementResult:
    """All normalized facial measurements."""

    # Face
    face_width: float = 0.0
    face_height: float = 0.0
    face_aspect_ratio: float = 0.0  # height / width

    # Eyes
    left_eye_width: float = 0.0
    right_eye_width: float = 0.0
    average_eye_width: float = 0.0
    inter_eye_distance: float = 0.0
    eye_face_width_ratio: float = 0.0

    # Nose
    nose_length: float = 0.0
    nose_width: float = 0.0
    nose_aspect_ratio: float = 0.0

    # Mouth
    mouth_width: float = 0.0
    mouth_nose_ratio: float = 0.0

    # Derived (used by golden ratio analysis)
    hairline_to_nose_base: float = 0.0

    def to_dict(self) -> dict[str, float]:
        """Convert to flat dictionary for scoring and API response."""
        return {
            "face_width": self.face_width,
            "face_height": self.face_height,
            "face_aspect_ratio": self.face_aspect_ratio,
            "left_eye_width": self.left_eye_width,
            "right_eye_width": self.right_eye_width,
            "average_eye_width": self.average_eye_width,
            "inter_eye_distance": self.inter_eye_distance,
            "eye_face_width_ratio": self.eye_face_width_ratio,
            "nose_length": self.nose_length,
            "nose_width": self.nose_width,
            "nose_aspect_ratio": self.nose_aspect_ratio,
            "mouth_width": self.mouth_width,
            "mouth_nose_ratio": self.mouth_nose_ratio,
            "hairline_to_nose_base": self.hairline_to_nose_base,
        }


def calculate_measurements(landmarks: FaceLandmarks) -> MeasurementResult:
    """
    Calculate all facial measurements from landmarks.

    All distances are normalized by face height.

    Args:
        landmarks: Extracted facial landmarks.

    Returns:
        MeasurementResult with all normalized measurements.
    """
    result = MeasurementResult()

    # --- Reference landmarks ---
    forehead = landmarks.get_landmark("forehead_top")
    chin = landmarks.get_landmark("chin")
    face_left = landmarks.get_landmark("face_left")
    face_right = landmarks.get_landmark("face_right")

    # --- Face dimensions ---
    raw_face_height = vertical_distance(forehead, chin)
    raw_face_width = horizontal_distance(face_left, face_right)

    # Use face height as the normalization reference
    ref = raw_face_height

    result.face_height = normalize_distance(raw_face_height, ref)  # Always 1.0
    result.face_width = normalize_distance(raw_face_width, ref)
    result.face_aspect_ratio = ratio(raw_face_height, raw_face_width)

    # --- Eye measurements ---
    left_eye_inner = landmarks.get_point(LANDMARK_INDICES["left_eye_inner"])
    left_eye_outer = landmarks.get_point(LANDMARK_INDICES["left_eye_outer"])
    right_eye_inner = landmarks.get_point(LANDMARK_INDICES["right_eye_inner"])
    right_eye_outer = landmarks.get_point(LANDMARK_INDICES["right_eye_outer"])

    raw_left_eye_width = distance(left_eye_outer, left_eye_inner)
    raw_right_eye_width = distance(right_eye_inner, right_eye_outer)
    raw_inter_eye = distance(left_eye_inner, right_eye_inner)

    result.left_eye_width = normalize_distance(raw_left_eye_width, ref)
    result.right_eye_width = normalize_distance(raw_right_eye_width, ref)
    result.average_eye_width = (result.left_eye_width + result.right_eye_width) / 2
    result.inter_eye_distance = normalize_distance(raw_inter_eye, ref)
    result.eye_face_width_ratio = ratio(
        (raw_left_eye_width + raw_right_eye_width) / 2, raw_face_width
    )

    # --- Nose measurements ---
    nose_bridge_top = landmarks.get_landmark("nose_bridge_top")
    nose_bottom = landmarks.get_landmark("nose_bottom")
    nose_left = landmarks.get_landmark("nose_left")
    nose_right = landmarks.get_landmark("nose_right")

    raw_nose_length = vertical_distance(nose_bridge_top, nose_bottom)
    raw_nose_width = horizontal_distance(nose_left, nose_right)

    result.nose_length = normalize_distance(raw_nose_length, ref)
    result.nose_width = normalize_distance(raw_nose_width, ref)
    result.nose_aspect_ratio = ratio(raw_nose_length, raw_nose_width)

    # --- Mouth measurements ---
    mouth_left = landmarks.get_landmark("mouth_left")
    mouth_right = landmarks.get_landmark("mouth_right")

    raw_mouth_width = horizontal_distance(mouth_left, mouth_right)

    result.mouth_width = normalize_distance(raw_mouth_width, ref)
    result.mouth_nose_ratio = ratio(raw_mouth_width, raw_nose_width)

    # --- Derived measurements ---
    result.hairline_to_nose_base = normalize_distance(
        vertical_distance(forehead, nose_bottom), ref
    )

    return result


# --- Proportion scoring ---

# Reference ranges for common facial proportions.
# Each tuple is (min_ideal, max_ideal) with center representing classical harmony.
PROPORTION_REFERENCES: dict[str, tuple[float, float]] = {
    "face_aspect_ratio": (1.35, 1.55),      # Classical target ~1.45
    "eye_face_width_ratio": (0.22, 0.26),  # Eyes ~24% of face width
    "nose_aspect_ratio": (1.10, 1.40),      # Nose length/width ~1.25
    "mouth_nose_ratio": (1.35, 1.65),      # Mouth typically ~1.5x nose width
    "inter_eye_distance": (0.18, 0.22),    # Inter-eye distance ~20% of face height
}


def calculate_proportion_score(measurements: MeasurementResult) -> float:
    """
    Calculate how close measured proportions are to classical reference ranges.

    Instead of awarding flat 100s to wide intervals, scores scale smoothly:
    - Ideal center point scores 100.
    - Within classical core range scores 85–100.
    - Deviations beyond core range scale down progressively (50–80).

    Returns:
        Proportion score (0–100).
    """
    meas_dict = measurements.to_dict()
    scores: list[float] = []

    for key, (ref_min, ref_max) in PROPORTION_REFERENCES.items():
        value = meas_dict.get(key, 0.0)
        if value <= 0:
            continue

        ideal = (ref_min + ref_max) / 2.0
        half_span = (ref_max - ref_min) / 2.0
        diff = abs(value - ideal)

        if diff <= half_span:
            # Smooth descent from 100.0 at ideal to 85.0 at core boundary
            score = 100.0 - 15.0 * (diff / half_span)
        else:
            # Steeper descent outside core range
            excess = diff - half_span
            rel_excess = excess / ideal
            score = max(0.0, 85.0 - rel_excess * 150.0)

        scores.append(score)

    return clamp(sum(scores) / len(scores)) if scores else 0.0
