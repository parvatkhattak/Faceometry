"""CLI prototype: python scripts/test_landmarks.py image.jpg [-o out.png]

Detects face landmarks, prints key coordinates, and saves an annotated image.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2  # noqa: E402

from app.cv.landmark_detector import LANDMARK_INDICES, LandmarkDetector  # noqa: E402
from app.cv.visualizer import draw_landmarks  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract and visualize facial landmarks.")
    parser.add_argument("image")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()

    image = cv2.imread(args.image)
    if image is None:
        print(f"Could not read image: {args.image}")
        return 1

    result = LandmarkDetector().detect(image)
    if not result.success:
        print(f"Detection failed ({result.face_count} faces): {result.error}")
        return 1

    lm = result.landmarks
    print(f"Detected {lm.count} landmarks")
    for name, idx in LANDMARK_INDICES.items():
        if isinstance(idx, int):
            p = lm.get_point(idx)
            print(f"  {name:<16} #{idx:<4} x={p.x:.4f} y={p.y:.4f}")

    out = args.output or str(Path(args.image).with_suffix("")) + "_landmarks.png"
    cv2.imwrite(out, draw_landmarks(image, lm))
    print(f"Annotated image saved to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
