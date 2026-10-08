"""
Image Quality & Pose Validator
===============================
Validates uploaded images before facial analysis.

Checks:
- Face count (exactly 1)
- Face size (reasonable portion of image)
- Blur detection (Laplacian variance)
- Lighting (brightness histogram)
- Head pose (yaw, pitch, roll within configurable thresholds)

All thresholds are configurable via app.config.settings.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np

from app.config import settings
from app.cv.landmark_detector import (
    DetectionResult,
    FaceLandmarks,
    LandmarkDetector,
    LANDMARK_INDICES,
    Point2D,
)

logger = logging.getLogger(__name__)


@dataclass
class PoseEstimate:
    """Estimated head pose in degrees."""
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0


@dataclass
class ValidationResult:
    """Result of image validation."""
    is_valid: bool = True
    issues: list[str] = field(default_factory=list)
    face_count: int = 0
    pose: Optional[PoseEstimate] = None
    landmarks: Optional[FaceLandmarks] = None
    detection_result: Optional[DetectionResult] = None

    def add_issue(self, issue: str) -> None:
        self.issues.append(issue)
        self.is_valid = False


class ImageValidator:
    """
    Validates an image for suitability in facial geometry analysis.

    Runs a pipeline of checks (face detection, blur, lighting, pose)
    and returns a structured ValidationResult.

    Usage:
        validator = ImageValidator()
        result = validator.validate(image_bgr)
        if not result.is_valid:
            print(result.issues)
    """

    def __init__(self, detector: Optional[LandmarkDetector] = None):
        self._detector = detector or LandmarkDetector()
        self._config = settings.validation

    def validate(self, image_bgr: np.ndarray) -> ValidationResult:
        """
        Run all validation checks on a BGR image.

        Args:
            image_bgr: OpenCV BGR image.

        Returns:
            ValidationResult with pass/fail and specific issues.
        """
        result = ValidationResult()

        # Basic image checks
        if image_bgr is None or image_bgr.size == 0:
            result.add_issue("Invalid or empty image.")
            return result

        h, w = image_bgr.shape[:2]
        if h < 100 or w < 100:
            result.add_issue("Image is too small. Minimum resolution is 100x100 pixels.")

        # Blur check
        self._check_blur(image_bgr, result)

        # Lighting check
        self._check_lighting(image_bgr, result)

        # Face detection + landmarks
        detection = self._detector.detect(image_bgr)
        result.detection_result = detection
        result.face_count = detection.face_count

        if detection.face_count == 0:
            result.add_issue("No face detected in the image.")
            return result

        if detection.face_count > 1:
            result.add_issue(
                f"Multiple faces detected ({detection.face_count}). "
                "Please use an image with exactly one face."
            )
            return result

        result.landmarks = detection.landmarks

        # Face size check
        self._check_face_size(detection.landmarks, h, w, result)

        # Pose estimation
        pose = self._estimate_pose(detection.landmarks)
        result.pose = pose
        self._check_pose(pose, result)

        return result

    def validate_from_bytes(self, image_bytes: bytes) -> ValidationResult:
        """Validate from raw image bytes."""
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            result = ValidationResult()
            result.add_issue("Failed to decode image. The file may be corrupt or in an unsupported format.")
            return result
        return self.validate(image)

    def _check_blur(self, image_bgr: np.ndarray, result: ValidationResult) -> None:
        """Detect blur using Laplacian variance."""
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var < self._config.blur_threshold:
            result.add_issue(
                f"Image appears too blurry (sharpness: {laplacian_var:.1f}, "
                f"minimum: {self._config.blur_threshold:.1f}). "
                "Please use a sharper photograph."
            )

    def _check_lighting(self, image_bgr: np.ndarray, result: ValidationResult) -> None:
        """Check for severe under/overexposure using mean brightness."""
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(np.mean(gray))

        if mean_brightness < self._config.min_brightness:
            result.add_issue(
                f"Image is too dark (brightness: {mean_brightness:.0f}/255). "
                "Please use a well-lit photograph."
            )
        elif mean_brightness > self._config.max_brightness:
            result.add_issue(
                f"Image is too bright/overexposed (brightness: {mean_brightness:.0f}/255). "
                "Please use a photograph with more balanced lighting."
            )

    def _check_face_size(
        self,
        landmarks: FaceLandmarks,
        img_height: int,
        img_width: int,
        result: ValidationResult,
    ) -> None:
        """Check that the face occupies a reasonable portion of the image."""
        # Get bounding box from landmarks
        xs = [lm.x for lm in landmarks.landmarks_2d]
        ys = [lm.y for lm in landmarks.landmarks_2d]

        face_width = (max(xs) - min(xs))
        face_height = (max(ys) - min(ys))
        face_area = face_width * face_height
        # Image area in normalized coords is 1.0
        image_area = 1.0

        face_fraction = face_area / image_area

        if face_fraction < self._config.min_face_fraction:
            result.add_issue(
                f"Face is too small in the image ({face_fraction:.1%} of frame). "
                "Please use a closer photograph or crop the image."
            )

    def _estimate_pose(self, landmarks: FaceLandmarks) -> PoseEstimate:
        """
        Estimate head pose from facial landmarks.

        Uses a simplified geometric approach based on key landmark positions
        to estimate yaw, pitch, and roll.
        """
        try:
            left_eye_outer = landmarks.get_point(LANDMARK_INDICES["left_eye_outer"])
            right_eye_outer = landmarks.get_point(LANDMARK_INDICES["right_eye_outer"])

            aspect = (
                landmarks.image_width / landmarks.image_height
                if landmarks.image_width > 0 and landmarks.image_height > 0
                else 1.0
            )

            # Roll estimation: angle of the line connecting the eyes (aspect-corrected)
            dx = (right_eye_outer.x - left_eye_outer.x) * aspect
            dy = right_eye_outer.y - left_eye_outer.y
            roll = math.degrees(math.atan2(dy, dx))

            # De-rotate key points by roll so head tilt doesn't falsely inflate yaw or pitch
            forehead = landmarks.get_landmark("forehead_top")
            chin = landmarks.get_landmark("chin")
            face_left = landmarks.get_landmark("face_left")
            face_right = landmarks.get_landmark("face_right")
            nose_tip = landmarks.get_landmark("nose_tip")

            cx = (forehead.x + chin.x) / 2
            cy = (forehead.y + chin.y) / 2
            roll_rad = math.radians(roll)
            cos_a = math.cos(-roll_rad)
            sin_a = math.sin(-roll_rad)

            def _rot(pt: Point2D) -> Point2D:
                xs = (pt.x - cx) * aspect
                ys = pt.y - cy
                rx = (xs * cos_a - ys * sin_a) / aspect + cx
                ry = xs * sin_a + ys * cos_a + cy
                return Point2D(x=rx, y=ry)

            r_face_left = _rot(face_left)
            r_face_right = _rot(face_right)
            r_nose_tip = _rot(nose_tip)
            r_forehead = _rot(forehead)
            r_chin = _rot(chin)

            # Yaw estimation in upright frame: compare nose position relative to face center
            face_center_x = (r_face_left.x + r_face_right.x) / 2
            face_width = abs(r_face_right.x - r_face_left.x)
            if face_width > 0:
                yaw_ratio = (r_nose_tip.x - face_center_x) / (face_width / 2)
                yaw = math.degrees(math.asin(max(-1.0, min(1.0, yaw_ratio))))
            else:
                yaw = 0.0

            # Pitch estimation in upright frame: compare nose position relative to face vertical center
            face_center_y = (r_forehead.y + r_chin.y) / 2
            face_height = abs(r_chin.y - r_forehead.y)
            if face_height > 0:
                pitch_ratio = (r_nose_tip.y - face_center_y) / (face_height / 2)
                pitch = math.degrees(math.asin(max(-1.0, min(1.0, pitch_ratio)))) * 0.5
            else:
                pitch = 0.0

            return PoseEstimate(yaw=round(yaw, 1), pitch=round(pitch, 1), roll=round(roll, 1))

        except Exception as e:
            logger.warning(f"Pose estimation failed: {e}")
            return PoseEstimate()

    def _check_pose(self, pose: PoseEstimate, result: ValidationResult) -> None:
        """Check that head pose is within acceptable thresholds."""
        issues = []

        if abs(pose.yaw) > self._config.max_yaw:
            issues.append(
                f"Face is turned too far sideways (yaw: {pose.yaw:.1f}°, "
                f"limit: ±{self._config.max_yaw:.0f}°)."
            )

        if abs(pose.pitch) > self._config.max_pitch:
            direction = "up" if pose.pitch < 0 else "down"
            issues.append(
                f"Face is tilted too far {direction} (pitch: {pose.pitch:.1f}°, "
                f"limit: ±{self._config.max_pitch:.0f}°)."
            )

        if abs(pose.roll) > self._config.max_roll:
            issues.append(
                f"Head is tilted sideways (roll: {pose.roll:.1f}°, "
                f"limit: ±{self._config.max_roll:.0f}°)."
            )

        if issues:
            result.add_issue(
                "Please use a more front-facing photograph. " + " ".join(issues)
            )
