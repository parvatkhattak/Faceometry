"""
Tests for geometry utility functions.
"""

import math
import pytest

from app.cv.landmark_detector import Point2D
from app.geometry.utils import (
    distance,
    horizontal_distance,
    vertical_distance,
    midpoint,
    angle,
    ratio,
    normalize_distance,
    reflect_point_across_line,
    centroid,
    clamp,
)


class TestDistance:
    def test_zero_distance(self):
        p = Point2D(0.5, 0.5)
        assert distance(p, p) == 0.0

    def test_unit_distance_horizontal(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(1.0, 0.0)
        assert distance(p1, p2) == pytest.approx(1.0)

    def test_unit_distance_vertical(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(0.0, 1.0)
        assert distance(p1, p2) == pytest.approx(1.0)

    def test_diagonal(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        assert distance(p1, p2) == pytest.approx(5.0)

    def test_symmetric(self):
        p1 = Point2D(0.1, 0.2)
        p2 = Point2D(0.5, 0.7)
        assert distance(p1, p2) == pytest.approx(distance(p2, p1))


class TestHorizontalVerticalDistance:
    def test_horizontal(self):
        p1 = Point2D(0.1, 0.5)
        p2 = Point2D(0.8, 0.5)
        assert horizontal_distance(p1, p2) == pytest.approx(0.7)

    def test_vertical(self):
        p1 = Point2D(0.5, 0.1)
        p2 = Point2D(0.5, 0.9)
        assert vertical_distance(p1, p2) == pytest.approx(0.8)

    def test_always_positive(self):
        p1 = Point2D(0.8, 0.9)
        p2 = Point2D(0.1, 0.2)
        assert horizontal_distance(p1, p2) > 0
        assert vertical_distance(p1, p2) > 0


class TestMidpoint:
    def test_simple_midpoint(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(1.0, 1.0)
        mid = midpoint(p1, p2)
        assert mid.x == pytest.approx(0.5)
        assert mid.y == pytest.approx(0.5)

    def test_same_point(self):
        p = Point2D(0.3, 0.7)
        mid = midpoint(p, p)
        assert mid.x == pytest.approx(0.3)
        assert mid.y == pytest.approx(0.7)


class TestAngle:
    def test_horizontal_right(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(1.0, 0.0)
        assert angle(p1, p2) == pytest.approx(0.0)

    def test_vertical_down(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(0.0, 1.0)
        assert angle(p1, p2) == pytest.approx(90.0)

    def test_45_degrees(self):
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(1.0, 1.0)
        assert angle(p1, p2) == pytest.approx(45.0)


class TestRatio:
    def test_simple_ratio(self):
        assert ratio(1.0, 2.0) == pytest.approx(0.5)

    def test_zero_denominator(self):
        assert ratio(5.0, 0.0) == 0.0

    def test_identity(self):
        assert ratio(3.0, 3.0) == pytest.approx(1.0)


class TestNormalizeDistance:
    def test_normalize(self):
        assert normalize_distance(0.5, 1.0) == pytest.approx(0.5)

    def test_normalize_half_reference(self):
        assert normalize_distance(0.5, 2.0) == pytest.approx(0.25)

    def test_zero_reference(self):
        assert normalize_distance(0.5, 0.0) == 0.0


class TestReflect:
    def test_reflect_across_vertical(self):
        """Reflect (0.3, 0.5) across x=0.5 vertical line → (0.7, 0.5)."""
        point = Point2D(0.3, 0.5)
        line_p1 = Point2D(0.5, 0.0)
        line_p2 = Point2D(0.5, 1.0)
        reflected = reflect_point_across_line(point, line_p1, line_p2)
        assert reflected.x == pytest.approx(0.7)
        assert reflected.y == pytest.approx(0.5)

    def test_reflect_point_on_line(self):
        """Reflecting a point already on the line returns the same point."""
        point = Point2D(0.5, 0.5)
        line_p1 = Point2D(0.5, 0.0)
        line_p2 = Point2D(0.5, 1.0)
        reflected = reflect_point_across_line(point, line_p1, line_p2)
        assert reflected.x == pytest.approx(0.5)
        assert reflected.y == pytest.approx(0.5)


class TestCentroid:
    def test_single_point(self):
        c = centroid([Point2D(0.3, 0.7)])
        assert c.x == pytest.approx(0.3)
        assert c.y == pytest.approx(0.7)

    def test_two_points(self):
        c = centroid([Point2D(0.0, 0.0), Point2D(1.0, 1.0)])
        assert c.x == pytest.approx(0.5)
        assert c.y == pytest.approx(0.5)

    def test_empty(self):
        c = centroid([])
        assert c.x == 0.0
        assert c.y == 0.0


class TestClamp:
    def test_within_range(self):
        assert clamp(50.0) == 50.0

    def test_below_min(self):
        assert clamp(-10.0) == 0.0

    def test_above_max(self):
        assert clamp(150.0) == 100.0
