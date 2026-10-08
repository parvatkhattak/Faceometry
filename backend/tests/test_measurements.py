"""Tests for facial measurements from known synthetic landmark coordinates."""

import pytest

from app.cv.landmark_detector import LANDMARK_INDICES as L, FaceLandmarks, Point3D
from app.geometry.measurements import calculate_measurements


def _face() -> FaceLandmarks:
    pts = [Point3D(x=0.5, y=0.5, z=0.0) for _ in range(468)]

    def put(name, x, y):
        pts[L[name]] = Point3D(x=x, y=y, z=0.0)

    put("forehead_top", 0.5, 0.1)
    put("chin", 0.5, 0.9)                    # face height 0.8
    put("face_left", 0.2, 0.5)
    put("face_right", 0.8, 0.5)              # face width 0.6
    put("left_eye_outer", 0.3, 0.4)
    put("left_eye_inner", 0.4, 0.4)          # eye width 0.1
    put("right_eye_inner", 0.6, 0.4)         # inter-eye 0.2
    put("right_eye_outer", 0.7, 0.4)         # eye width 0.1
    return FaceLandmarks(landmarks_3d=pts, image_width=100, image_height=100)


class TestMeasurements:
    def test_face_dimensions_normalized_by_height(self):
        m = calculate_measurements(_face())
        assert m.face_height == pytest.approx(1.0)
        assert m.face_width == pytest.approx(0.6 / 0.8, abs=1e-3)
        assert m.face_aspect_ratio == pytest.approx(0.8 / 0.6, abs=1e-3)

    def test_eye_measurements(self):
        m = calculate_measurements(_face())
        assert m.average_eye_width == pytest.approx(0.1 / 0.8, abs=1e-3)
        assert m.inter_eye_distance == pytest.approx(0.2 / 0.8, abs=1e-3)
        assert m.eye_face_width_ratio == pytest.approx(0.1 / 0.6, abs=1e-3)

    def test_to_dict_has_all_keys(self):
        d = calculate_measurements(_face()).to_dict()
        assert {"face_width", "inter_eye_distance", "mouth_width", "hairline_to_nose_base"} <= d.keys()

    def test_calculate_proportion_score(self):
        from app.geometry.measurements import calculate_proportion_score
        m = calculate_measurements(_face())
        score = calculate_proportion_score(m)
        assert 0.0 <= score <= 100.0
