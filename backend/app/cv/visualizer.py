"""
Facial Landmark Visualizer
===========================
Draws facial landmarks, connections, and annotations over images
for debugging and results display.
"""

from __future__ import annotations

import cv2
import numpy as np

from app.cv.landmark_detector import FaceLandmarks, LANDMARK_INDICES


# Color palette (BGR format)
COLORS = {
    "landmark": (0, 255, 200),       # Cyan-green dots
    "jaw": (200, 200, 200),          # Light gray
    "left_eye": (255, 200, 50),      # Light blue
    "right_eye": (255, 200, 50),     # Light blue
    "left_eyebrow": (100, 255, 100), # Green
    "right_eyebrow": (100, 255, 100),# Green
    "nose": (50, 200, 255),          # Orange-yellow
    "mouth": (50, 50, 255),          # Red
    "midline": (255, 100, 255),      # Magenta
    "symmetry": (0, 165, 255),       # Orange
}


def draw_landmarks(
    image: np.ndarray,
    landmarks: FaceLandmarks,
    draw_all_points: bool = True,
    draw_regions: bool = True,
    draw_midline: bool = True,
    point_radius: int = 1,
    line_thickness: int = 1,
) -> np.ndarray:
    """
    Draw facial landmarks on an image.

    Args:
        image: BGR image (will be copied, not modified in place).
        landmarks: Extracted facial landmarks.
        draw_all_points: Draw all 468 landmark points.
        draw_regions: Draw region-specific connections.
        draw_midline: Draw the estimated facial midline.
        point_radius: Radius of landmark dots.
        line_thickness: Thickness of connection lines.

    Returns:
        Annotated image copy.
    """
    annotated = image.copy()
    h, w = annotated.shape[:2]

    # Draw all points
    if draw_all_points:
        for lm in landmarks.landmarks_2d:
            px, py = lm.to_pixel(w, h)
            cv2.circle(annotated, (px, py), point_radius, COLORS["landmark"], -1)

    # Draw specific regions with connections
    if draw_regions:
        _draw_region_connections(annotated, landmarks, "jaw", COLORS["jaw"], line_thickness, closed=False)
        _draw_region_connections(annotated, landmarks, "left_eye", COLORS["left_eye"], line_thickness, closed=True)
        _draw_region_connections(annotated, landmarks, "right_eye", COLORS["right_eye"], line_thickness, closed=True)
        _draw_region_connections(annotated, landmarks, "left_eyebrow", COLORS["left_eyebrow"], line_thickness, closed=False)
        _draw_region_connections(annotated, landmarks, "right_eyebrow", COLORS["right_eyebrow"], line_thickness, closed=False)
        _draw_region_connections(annotated, landmarks, "nose_bridge", COLORS["nose"], line_thickness, closed=False)
        _draw_region_connections(annotated, landmarks, "mouth_outer", COLORS["mouth"], line_thickness, closed=True)

    # Draw midline
    if draw_midline:
        midline_indices = LANDMARK_INDICES["midline"]
        for i in range(len(midline_indices) - 1):
            pt1 = landmarks.get_pixel_point(midline_indices[i])
            pt2 = landmarks.get_pixel_point(midline_indices[i + 1])
            cv2.line(annotated, pt1, pt2, COLORS["midline"], line_thickness, cv2.LINE_AA)

    return annotated


def _draw_region_connections(
    image: np.ndarray,
    landmarks: FaceLandmarks,
    region_name: str,
    color: tuple[int, int, int],
    thickness: int,
    closed: bool = False,
) -> None:
    """Draw connected lines through a named region's landmarks."""
    indices = LANDMARK_INDICES.get(region_name)
    if indices is None or isinstance(indices, int):
        return

    w, h = landmarks.image_width, landmarks.image_height
    points = [landmarks.get_point(i).to_pixel(w, h) for i in indices]

    for i in range(len(points) - 1):
        cv2.line(image, points[i], points[i + 1], color, thickness, cv2.LINE_AA)

    if closed and len(points) > 2:
        cv2.line(image, points[-1], points[0], color, thickness, cv2.LINE_AA)


def draw_measurement_line(
    image: np.ndarray,
    landmarks: FaceLandmarks,
    index1: int,
    index2: int,
    color: tuple[int, int, int] = (0, 255, 255),
    thickness: int = 2,
    label: str | None = None,
) -> np.ndarray:
    """Draw a measurement line between two landmarks with optional label."""
    annotated = image.copy()
    pt1 = landmarks.get_pixel_point(index1)
    pt2 = landmarks.get_pixel_point(index2)

    cv2.line(annotated, pt1, pt2, color, thickness, cv2.LINE_AA)

    # Draw endpoints
    cv2.circle(annotated, pt1, 3, color, -1)
    cv2.circle(annotated, pt2, 3, color, -1)

    # Draw label at midpoint
    if label:
        mid_x = (pt1[0] + pt2[0]) // 2
        mid_y = (pt1[1] + pt2[1]) // 2
        cv2.putText(
            annotated, label, (mid_x + 5, mid_y - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA,
        )

    return annotated


def encode_image_to_base64(image: np.ndarray, format: str = ".png") -> str:
    """Encode an OpenCV image to a base64 data URI string."""
    import base64

    _, buffer = cv2.imencode(format, image)
    encoded = base64.b64encode(buffer).decode("utf-8")
    mime = "image/png" if format == ".png" else "image/jpeg"
    return f"data:{mime};base64,{encoded}"
