# Faceometry Architecture

## High-Level Architecture

```
                         USER
                           │
                           ▼
                    Next.js Frontend
                           │
                     Image Upload
                           │
                           ▼
                      FastAPI API
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       Image Validation            Face Detection
             │                           │
             └─────────────┬─────────────┘
                           ▼
                  MediaPipe Face
                    Landmarker
                           │
                           ▼
                  Facial Landmarks
                           │
                           ▼
                  Geometry Engine
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Symmetry        Proportions      Golden Ratio
      Analysis         Analysis          Analysis
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    Scoring Engine
                           │
                           ▼
                 Facial Harmony Score
                           │
                           ▼
                    JSON Response
                           │
                           ▼
                   Next.js Dashboard
```

## Module Dependency Graph

```
app/
├── main.py              → FastAPI app, imports api/
├── config.py            → Pydantic settings (no internal deps)
├── api/
│   └── analyze.py       → imports services/
├── services/
│   └── analysis.py      → imports cv/, geometry/, scoring/
├── cv/
│   ├── landmark_detector.py  → MediaPipe wrapper
│   ├── face_detector.py      → imports landmark_detector
│   ├── image_validator.py    → imports face_detector, config
│   └── visualizer.py         → imports landmark_detector
├── geometry/
│   ├── utils.py              → pure math (no internal deps)
│   ├── measurements.py       → imports utils
│   ├── symmetry.py           → imports utils
│   ├── golden_ratio.py       → imports utils, config
│   ├── thirds.py             → imports utils, config
│   └── fifths.py             → imports utils
├── scoring/
│   └── engine.py             → imports config
└── models/
    └── schemas.py            → Pydantic models (no internal deps)
```

## Data Flow

1. **Image Upload** → multipart/form-data to `/api/analyze`
2. **Validation** → file type, size, blur, lighting, face count, pose
3. **Landmark Extraction** → MediaPipe 468-point face mesh
4. **Geometry** → normalized measurements from landmarks
5. **Analysis** → symmetry, proportions, golden ratio, thirds, fifths
6. **Scoring** → weighted combination → Facial Harmony Score
7. **Response** → structured JSON with scores, measurements, explanations
8. **Cleanup** → image deleted from memory (never persisted)
