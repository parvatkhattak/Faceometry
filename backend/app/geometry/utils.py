"""
Geometry Utilities
==================
Pure mathematical functions for facial geometry calculations.

All functions operate on normalized coordinates and are
independent of image resolution or face size.

These are the building blocks used by every analysis module.
"""

from __future__ import annotations

import math
from typing import Union

import numpy as np

from app.cv.landmark_detector import Point2D


def distance(p1: Point2D, p2: Point2D) -> float:
    """
    Euclidean distance between two 2D points.

    Args:
        p1: First point (normalized coordinates).
        p2: Second point (normalized coordinates).

    Returns:
        Euclidean distance.
    """
    return math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)


def horizontal_distance(p1: Point2D, p2: Point2D) -> float:
    """
    Horizontal (x-axis) distance between two points.

    Returns:
        Absolute horizontal distance.
    """
    return abs(p2.x - p1.x)


def vertical_distance(p1: Point2D, p2: Point2D) -> float:
    """
    Vertical (y-axis) distance between two points.

    Returns:
        Absolute vertical distance.
    """
    return abs(p2.y - p1.y)


def midpoint(p1: Point2D, p2: Point2D) -> Point2D:
    """
    Midpoint between two 2D points.

    Returns:
        Point2D at the geometric center.
    """
    return Point2D(
        x=(p1.x + p2.x) / 2,
        y=(p1.y + p2.y) / 2,
    )


def angle(p1: Point2D, p2: Point2D) -> float:
    """
    Angle in degrees of the line from p1 to p2 relative to the horizontal.

    Returns:
        Angle in degrees (range: -180 to 180).
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    return math.degrees(math.atan2(dy, dx))


def ratio(numerator: float, denominator: float) -> float:
    """
    Safe division returning the ratio of two values.

    Returns 0.0 if denominator is zero or near-zero.
    """
    if abs(denominator) < 1e-10:
        return 0.0
    return numerator / denominator


def normalize_distance(d: float, reference: float) -> float:
    """
    Normalize a distance by a reference dimension.

    d_normalized = d / D_reference

    This makes measurements independent of image resolution
    and face size.

    Args:
        d: Raw distance to normalize.
        reference: Reference dimension (e.g., face height).

    Returns:
        Normalized distance. Returns 0.0 if reference is zero.
    """
    if abs(reference) < 1e-10:
        return 0.0
    return d / reference


def reflect_point_across_line(
    point: Point2D,
    line_point1: Point2D,
    line_point2: Point2D,
) -> Point2D:
    """
    Reflect a point across a line defined by two points.

    Used for symmetry analysis: reflect left-side landmarks
    across the facial midline to compare with right-side landmarks.

    Args:
        point: The point to reflect.
        line_point1: First point defining the reflection axis.
        line_point2: Second point defining the reflection axis.

    Returns:
        Reflected Point2D.
    """
    # Direction vector of the line
    dx = line_point2.x - line_point1.x
    dy = line_point2.y - line_point1.y
    line_len_sq = dx * dx + dy * dy

    if line_len_sq < 1e-12:
        return point  # Degenerate line

    # Project point onto line
    t = ((point.x - line_point1.x) * dx + (point.y - line_point1.y) * dy) / line_len_sq

    # Projection point
    proj_x = line_point1.x + t * dx
    proj_y = line_point1.y + t * dy

    # Reflection = 2 * projection - original
    return Point2D(
        x=2 * proj_x - point.x,
        y=2 * proj_y - point.y,
    )


def centroid(points: list[Point2D]) -> Point2D:
    """
    Calculate the geometric centroid of a set of points.

    Args:
        points: List of 2D points.

    Returns:
        Centroid as a Point2D.
    """
    if not points:
        return Point2D(0.0, 0.0)

    mean_x = sum(p.x for p in points) / len(points)
    mean_y = sum(p.y for p in points) / len(points)
    return Point2D(x=mean_x, y=mean_y)


def polygon_perimeter(points: list[Point2D]) -> float:
    """Calculate the perimeter of a polygon defined by ordered points."""
    if len(points) < 2:
        return 0.0
    total = sum(distance(points[i], points[i + 1]) for i in range(len(points) - 1))
    total += distance(points[-1], points[0])  # Close the polygon
    return total


def clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp a value to a range."""
    return max(min_val, min(max_val, value))
