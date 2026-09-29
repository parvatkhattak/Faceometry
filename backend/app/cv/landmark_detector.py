"""
MediaPipe Facial Landmark Detector
===================================
Wraps MediaPipe Face Landmarker to provide a clean interface for
extracting 468-point facial landmarks from images.

This module is the foundation of the entire CV pipeline —
all geometry, symmetry, and scoring modules depend on its output.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

logger = logging.getLogger(__name__)

# MediaPipe Face Mesh landmark indices for key facial regions.
# Full mesh has 468 landmarks. These indices map to anatomically
# meaningful points used by the geometry engine.
#
# Reference: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png

LANDMARK_INDICES = {
    # Face contour (jawline)
    "jaw": [
        10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
        172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
    ],

    # Left eye (from viewer's perspective — person's right eye)
    "left_eye": [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
    "left_eye_inner": 133,
    "left_eye_outer": 33,

    # Right eye (from viewer's perspective — person's left eye)
    "right_eye": [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
    "right_eye_inner": 362,
    "right_eye_outer": 263,

    # Left eyebrow
    "left_eyebrow": [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],

    # Right eyebrow
    "right_eyebrow": [300, 293, 334, 296, 336, 285, 295, 282, 283, 276],

    # Nose
    "nose_tip": 1,
    "nose_bridge_top": 6,
    "nose_bottom": 2,
    "nose_left": 129,   # Left alar (nostril wing)
    "nose_right": 358,  # Right alar (nostril wing)
    "nose_bridge": [6, 197, 195, 5, 4, 1],

    # Mouth
    "mouth_left": 61,
    "mouth_right": 291,
    "upper_lip_top": 0,
    "lower_lip_bottom": 17,
    "mouth_outer": [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146],

    # Chin
    "chin": 152,

    # Forehead approximation (top of face mesh)
    "forehead_top": 10,

    # Face boundaries (leftmost/rightmost points)
    "face_left": 234,   # Leftmost point of face contour
    "face_right": 454,  # Rightmost point of face contour

    # Facial midline landmarks (for symmetry axis)
    "midline": [10, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 2, 164, 0, 17, 152],

    # Iris centers (if available in the mesh)
    "left_iris_center": 468,   # Available in face mesh with iris
    "right_iris_center": 473,  # Available in face mesh with iris
}


@dataclass
class Point2D:
    """A 2D point in normalized [0, 1] coordinates."""
    x: float
    y: float

    def to_pixel(self, width: int, height: int) -> tuple[int, int]:
        """Convert normalized coordinates to pixel coordinates."""
        return int(self.x * width), int(self.y * height)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y])


@dataclass
class Point3D:
    """A 3D point in normalized coordinates."""
    x: float
    y: float
    z: float

    def to_2d(self) -> Point2D:
        return Point2D(x=self.x, y=self.y)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])


@dataclass
class FaceLandmarks:
    """Extracted facial landmarks with convenience accessors."""
    landmarks_3d: list[Point3D] = field(default_factory=list)
    image_width: int = 0
    image_height: int = 0

    @property
    def landmarks_2d(self) -> list[Point2D]:
        """Get 2D projection of all landmarks."""
        return [lm.to_2d() for lm in self.landmarks_3d]

    @property
    def count(self) -> int:
        return len(self.landmarks_3d)

    def get_point(self, index: int) -> Point2D:
        """Get a single landmark as a 2D point by index."""
        lm = self.landmarks_3d[index]
        return Point2D(x=lm.x, y=lm.y)

    def get_point_3d(self, index: int) -> Point3D:
        """Get a single landmark as a 3D point by index."""
        return self.landmarks_3d[index]

    def get_points(self, indices: list[int]) -> list[Point2D]:
        """Get multiple landmarks as 2D points by indices."""
        return [self.get_point(i) for i in indices]

    def get_pixel_point(self, index: int) -> tuple[int, int]:
        """Get a landmark as pixel coordinates."""
        return self.get_point(index).to_pixel(self.image_width, self.image_height)

    def get_region(self, region_name: str) -> list[Point2D]:
        """Get landmarks for a named facial region."""
        indices = LANDMARK_INDICES.get(region_name)
        if indices is None:
            raise ValueError(f"Unknown region: {region_name}")
        if isinstance(indices, int):
            return [self.get_point(indices)]
        return self.get_points(indices)

    def get_landmark(self, landmark_name: str) -> Point2D:
        """Get a single named landmark."""
        index = LANDMARK_INDICES.get(landmark_name)
        if index is None:
            raise ValueError(f"Unknown landmark: {landmark_name}")
        if isinstance(index, list):
            raise ValueError(f"'{landmark_name}' is a region, not a single landmark. Use get_region().")
        return self.get_point(index)


@dataclass
class DetectionResult:
    """Result of face detection and landmark extraction."""
    face_count: int
    landmarks: Optional[FaceLandmarks] = None
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.face_count == 1 and self.landmarks is not None


class LandmarkDetector:
    """
    MediaPipe Face Landmarker wrapper.

    Provides a clean interface for detecting faces and extracting
    dense facial landmarks from images.

    Usage:
        detector = LandmarkDetector()
        result = detector.detect(image_bgr)
        if result.success:
            landmarks = result.landmarks
    """

    def __init__(self, model_path: Optional[str] = None, min_detection_confidence: float = 0.5):
        """
        Initialize the landmark detector.

        Args:
            model_path: Path to the MediaPipe face landmarker model.
                        If None, uses the default bundled model.
            min_detection_confidence: Minimum confidence for face detection.
        """
        self._model_path = model_path
        self._min_detection_confidence = min_detection_confidence
        self._detector: Optional[vision.FaceLandmarker] = None

    def _ensure_model(self) -> None:
        """Download the model if not already present, and initialize detector."""
        if self._detector is not None:
            return

        if self._model_path and Path(self._model_path).exists():
            model_path = self._model_path
        else:
            # Use the default MediaPipe face landmarker model
            model_path = self._download_default_model()

        base_options = mp_python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=5,  # Detect up to 5 to count and reject multi-face
            min_face_detection_confidence=self._min_detection_confidence,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,  # For pose estimation
        )
        self._detector = vision.FaceLandmarker.create_from_options(options)

    @staticmethod
    def _download_default_model() -> str:
        """Download the default MediaPipe face landmarker model if needed."""
        import urllib.request

        model_dir = Path(__file__).parent / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / "face_landmarker_v2_with_blendshapes.task"

        if model_path.exists():
            return str(model_path)

        url = (
            "https://storage.googleapis.com/mediapipe-models/"
            "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
        )
        logger.info("Downloading MediaPipe face landmarker model...")
        urllib.request.urlretrieve(url, str(model_path))
        logger.info(f"Model downloaded to {model_path}")
        return str(model_path)

    def detect(self, image_bgr: np.ndarray) -> DetectionResult:
        """
        Detect faces and extract landmarks from a BGR image.

        Args:
            image_bgr: OpenCV BGR image (numpy array).

        Returns:
            DetectionResult with face count and landmarks (if exactly 1 face).
        """
        self._ensure_model()

        # Convert BGR to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

        try:
            result = self._detector.detect(mp_image)
        except Exception as e:
            logger.error(f"MediaPipe detection failed: {e}")
            return DetectionResult(face_count=0, error=f"Face detection failed: {str(e)}")

        face_count = len(result.face_landmarks)

        if face_count == 0:
            return DetectionResult(face_count=0, error="No face detected.")

        if face_count > 1:
            return DetectionResult(
                face_count=face_count,
                error=f"Multiple faces detected ({face_count}). Please use an image with exactly one face.",
            )

        # Extract landmarks from the single detected face
        face_lms = result.face_landmarks[0]
        height, width = image_bgr.shape[:2]

        landmarks_3d = [
            Point3D(x=lm.x, y=lm.y, z=lm.z)
            for lm in face_lms
        ]

        face_landmarks = FaceLandmarks(
            landmarks_3d=landmarks_3d,
            image_width=width,
            image_height=height,
        )

        return DetectionResult(
            face_count=1,
            landmarks=face_landmarks,
        )

    def detect_from_file(self, image_path: str) -> DetectionResult:
        """
        Detect faces from an image file path.

        Args:
            image_path: Path to the image file.

        Returns:
            DetectionResult with face count and landmarks.
        """
        image = cv2.imread(image_path)
        if image is None:
            return DetectionResult(face_count=0, error=f"Failed to read image: {image_path}")
        return self.detect(image)

    def detect_from_bytes(self, image_bytes: bytes) -> DetectionResult:
        """
        Detect faces from raw image bytes.

        Args:
            image_bytes: Raw image file bytes (JPEG, PNG, etc.).

        Returns:
            DetectionResult with face count and landmarks.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            return DetectionResult(face_count=0, error="Failed to decode image from bytes.")
        return self.detect(image)
