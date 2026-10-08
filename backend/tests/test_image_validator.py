"""Unit tests for image validator and pose estimation/alignment."""

import math
import pytest
from app.config import settings
from app.cv.image_validator import ImageValidator, PoseEstimate, ValidationResult
from app.cv.landmark_detector import FaceLandmarks, Point3D, LANDMARK_INDICES
from app.geometry.fifths import analyze_facial_fifths
from app.geometry.thirds import analyze_facial_thirds


def _synthetic_face(angle_deg: float = 0.0) -> FaceLandmarks:
    """Create a synthetic face rotated by angle_deg around center (0.5, 0.5)."""
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    cx, cy = 0.5, 0.5

    def _rot(x: float, y: float) -> tuple[float, float]:
        dx = x - cx
        dy = y - cy
        rx = dx * cos_a - dy * sin_a + cx
        ry = dx * sin_a + dy * cos_a + cy
        return rx, ry

    pts = [Point3D(x=0.5, y=0.5, z=0.0) for _ in range(468)]

    # Upright landmarks
    upright = {
        "forehead_top": (0.5, 0.2),
        "chin": (0.5, 0.8),
        "nose_bottom": (0.5, 0.6),
        "nose_tip": (0.5, 0.55),
        "face_left": (0.2, 0.5),
        "face_right": (0.8, 0.5),
        "left_eye_outer": (0.35, 0.4),
        "right_eye_outer": (0.65, 0.4),
    }

    for name, (x, y) in upright.items():
        rx, ry = _rot(x, y)
        idx = LANDMARK_INDICES[name]
        pts[idx] = Point3D(x=rx, y=ry, z=0.0)

    # Eyebrows at y=0.4
    for key in ("left_eyebrow", "right_eyebrow"):
        for i in LANDMARK_INDICES[key]:
            rx, ry = _rot(0.5, 0.4)
            pts[i] = Point3D(x=rx, y=ry, z=0.0)

    return FaceLandmarks(landmarks_3d=pts, image_width=500, image_height=500)


class TestPoseValidationThresholds:
    def test_moderate_tilt_is_accepted(self):
        validator = ImageValidator()
        res = ValidationResult()
        # Moderate roll of 20° (under 35°)
        validator._check_pose(PoseEstimate(yaw=15.0, pitch=15.0, roll=20.0), res)
        assert res.is_valid
        assert len(res.issues) == 0

    def test_extreme_tilt_is_rejected(self):
        validator = ImageValidator()
        res = ValidationResult()
        # Extreme roll of 40° (exceeds 35°)
        validator._check_pose(PoseEstimate(yaw=0.0, pitch=0.0, roll=40.0), res)
        assert not res.is_valid
        assert any("Head is tilted sideways" in issue for issue in res.issues)

    def test_moderate_yaw_is_accepted(self):
        validator = ImageValidator()
        res = ValidationResult()
        # 25° yaw (under 30°)
        validator._check_pose(PoseEstimate(yaw=25.0, pitch=0.0, roll=0.0), res)
        assert res.is_valid

    def test_extreme_yaw_is_rejected(self):
        validator = ImageValidator()
        res = ValidationResult()
        # 35° yaw (exceeds 30°)
        validator._check_pose(PoseEstimate(yaw=35.0, pitch=0.0, roll=0.0), res)
        assert not res.is_valid
        assert any("turned too far sideways" in issue for issue in res.issues)


class TestLandmarkAlignment:
    def test_align_upright_straightens_tilted_face(self):
        # Face tilted by 20 degrees
        tilted_face = _synthetic_face(angle_deg=20.0)
        aligned_face = tilted_face.align_upright()

        # In aligned face, the eyes should be horizontal (dy ≈ 0)
        left_eye = aligned_face.get_point(LANDMARK_INDICES["left_eye_outer"])
        right_eye = aligned_face.get_point(LANDMARK_INDICES["right_eye_outer"])

        assert abs(right_eye.y - left_eye.y) < 1e-4
        assert right_eye.x > left_eye.x

    def test_align_upright_preserves_already_upright_face(self):
        upright = _synthetic_face(angle_deg=0.0)
        aligned = upright.align_upright()

        p1 = upright.get_point(LANDMARK_INDICES["chin"])
        p2 = aligned.get_point(LANDMARK_INDICES["chin"])
        assert abs(p1.x - p2.x) < 1e-4
        assert abs(p1.y - p2.y) < 1e-4
