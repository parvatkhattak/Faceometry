"""Tests for facial thirds and fifths using synthetic landmarks."""

from app.cv.landmark_detector import LANDMARK_INDICES, FaceLandmarks, Point3D
from app.geometry.fifths import analyze_facial_fifths
from app.geometry.thirds import analyze_facial_thirds


def _blank() -> list[Point3D]:
    return [Point3D(x=0.5, y=0.5, z=0.0) for _ in range(468)]


def _set(pts, idx, x=None, y=None):
    p = pts[idx]
    pts[idx] = Point3D(x=p.x if x is None else x, y=p.y if y is None else y, z=0.0)


def _face_with_thirds(brow_y: float, nose_y: float) -> FaceLandmarks:
    pts = _blank()
    _set(pts, LANDMARK_INDICES["forehead_top"], y=0.0)
    _set(pts, LANDMARK_INDICES["chin"], y=1.0)
    _set(pts, LANDMARK_INDICES["nose_bottom"], y=nose_y)
    for key in ("left_eyebrow", "right_eyebrow"):
        for i in LANDMARK_INDICES[key]:
            _set(pts, i, y=brow_y)
    return FaceLandmarks(landmarks_3d=pts, image_width=100, image_height=100)


def _face_with_fifths(xs: list[float]) -> FaceLandmarks:
    pts = _blank()
    names = [
        LANDMARK_INDICES["face_left"], LANDMARK_INDICES["left_eye_outer"],
        LANDMARK_INDICES["left_eye_inner"], LANDMARK_INDICES["right_eye_inner"],
        LANDMARK_INDICES["right_eye_outer"], LANDMARK_INDICES["face_right"],
    ]
    for idx, x in zip(names, xs):
        _set(pts, idx, x=x)
    return FaceLandmarks(landmarks_3d=pts, image_width=100, image_height=100)


class TestThirds:
    def test_equal_thirds_score_high(self):
        r = analyze_facial_thirds(_face_with_thirds(1 / 3, 2 / 3))
        assert abs(r.upper_third - 1 / 3) < 1e-3
        assert r.score > 99

    def test_unequal_thirds_score_lower(self):
        r = analyze_facial_thirds(_face_with_thirds(0.1, 0.9))
        assert r.score < analyze_facial_thirds(_face_with_thirds(1 / 3, 2 / 3)).score

    def test_proportions_sum_to_one(self):
        r = analyze_facial_thirds(_face_with_thirds(0.3, 0.6))
        assert abs(r.upper_third + r.middle_third + r.lower_third - 1.0) < 2e-3


class TestFifths:
    def test_equal_fifths_score_high(self):
        r = analyze_facial_fifths(_face_with_fifths([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
        assert all(abs(s - 0.2) < 1e-6 for s in r.sections)
        assert r.score > 99

    def test_unequal_fifths_score_lower(self):
        r = analyze_facial_fifths(_face_with_fifths([0.0, 0.1, 0.2, 0.8, 0.9, 1.0]))
        assert r.score < 90
