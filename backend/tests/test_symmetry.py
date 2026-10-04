"""Tests for symmetry analysis using synthetic landmark sets."""

import random

from app.cv.landmark_detector import FaceLandmarks, Point3D
from app.geometry.symmetry import BILATERAL_PAIRS, analyze_symmetry


def _symmetric_face(jitter: float = 0.0, seed: int = 0) -> FaceLandmarks:
    """Build 468 landmarks mirrored about x=0.5; optionally perturb the right side."""
    rng = random.Random(seed)
    pts = [Point3D(x=0.5, y=0.5, z=0.0) for _ in range(468)]
    pts[10] = Point3D(x=0.5, y=0.1, z=0.0)   # forehead top
    pts[152] = Point3D(x=0.5, y=0.9, z=0.0)  # chin
    for left, right, _ in BILATERAL_PAIRS:
        for i, (l, r) in enumerate(zip(left, right)):
            y = 0.3 + 0.04 * i
            dx = 0.1 + 0.02 * i
            pts[l] = Point3D(x=0.5 - dx, y=y, z=0.0)
            pts[r] = Point3D(
                x=0.5 + dx + rng.uniform(-jitter, jitter),
                y=y + rng.uniform(-jitter, jitter),
                z=0.0,
            )
    # Shared/midline landmarks (10 appears in both jaw lists, 5 in both nose lists)
    pts[10] = Point3D(x=0.5, y=0.1, z=0.0)
    pts[152] = Point3D(x=0.5, y=0.9, z=0.0)
    pts[5] = Point3D(x=0.5, y=0.5, z=0.0)
    return FaceLandmarks(landmarks_3d=pts, image_width=100, image_height=100)


class TestSymmetry:
    def test_perfect_symmetry(self):
        result = analyze_symmetry(_symmetric_face())
        assert result.overall_score > 99

    def test_asymmetry_lowers_score(self):
        assert analyze_symmetry(_symmetric_face(0.03)).overall_score < \
            analyze_symmetry(_symmetric_face(0.0)).overall_score

    def test_all_regions_reported(self):
        result = analyze_symmetry(_symmetric_face())
        assert {d.region for d in result.details} == {"eyes", "eyebrows", "nose", "mouth", "jawline", "cheeks"}

    def test_eye_pairs_are_mirror_ordered(self):
        """Left outer corner (33) must pair with right outer corner (263), inner with inner."""
        left, right, name = BILATERAL_PAIRS[0]
        assert name == "eyes"
        assert (left[0], right[0]) == (33, 263)
        assert (left[-1], right[-1]) == (133, 362)
