# Faceometry API Reference

## Endpoints

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### `POST /api/analyze`

Analyze a facial photograph.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `image` field containing JPEG, PNG, or WebP file (max 10 MB)

**Success Response (200):**
```json
{
  "success": true,
  "face": {
    "count": 1,
    "pose": {
      "yaw": 2.1,
      "pitch": -1.8,
      "roll": 0.4
    }
  },
  "scores": {
    "symmetry": 87.2,
    "proportion": 81.7,
    "golden_ratio": 76.4,
    "facial_thirds": 84.8,
    "facial_fifths": 80.1,
    "harmony": 82.3
  },
  "measurements": {
    "face_width": 1.0,
    "face_height": 1.42,
    "face_aspect_ratio": 1.42,
    "left_eye_width": 0.22,
    "right_eye_width": 0.21,
    "..."
  },
  "golden_ratio_analysis": {
    "ratios": [
      {
        "name": "Face Height / Face Width",
        "value": 1.42,
        "target": 1.618,
        "deviation": 0.122,
        "score": 87.8
      }
    ],
    "overall_score": 76.4
  },
  "symmetry_analysis": {
    "overall_score": 87.2,
    "details": [
      {
        "region": "eyes",
        "error": 0.012,
        "score": 91.3
      }
    ]
  },
  "facial_thirds": {
    "upper_third": 0.31,
    "middle_third": 0.34,
    "lower_third": 0.35,
    "score": 84.8
  },
  "facial_fifths": {
    "sections": [0.19, 0.21, 0.20, 0.21, 0.19],
    "score": 80.1
  },
  "explanations": [
    {
      "component": "Symmetry",
      "score": 87.2,
      "explanation": "Your facial landmarks show relatively low left-right deviation."
    }
  ],
  "landmark_image_base64": "data:image/png;base64,..."
}
```

**Error Responses:**

- `400` — Invalid file type or corrupt image
- `422` — Validation failed (no face, multiple faces, blur, pose)
- `413` — File too large
- `500` — Internal server error

```json
{
  "success": false,
  "error": "No face detected in the uploaded image.",
  "detail": null
}
```
