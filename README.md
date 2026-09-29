# Faceometry

## The Geometry Behind Your Face

**Analyze your facial proportions, symmetry, and classical geometric ratios using computer vision and mathematics.**

Faceometry is an AI-powered facial geometry and symmetry analysis platform that uses computer vision, mathematical proportions, and machine learning to analyze facial structure and harmony.

> **Important:** Faceometry is a geometric analysis tool. It does not claim to objectively measure beauty or attractiveness.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js, TypeScript, Tailwind CSS |
| **Backend** | Python, FastAPI, Pydantic |
| **Computer Vision** | MediaPipe Face Landmarker, OpenCV |
| **Math/Science** | NumPy, custom geometry engine |
| **Deployment** | Docker, Vercel (frontend), Render/Railway (backend) |

---

## Project Structure

```
faceometry/
├── frontend/          # Next.js + TypeScript + Tailwind
├── backend/           # FastAPI + MediaPipe + Geometry Engine
│   ├── app/
│   │   ├── api/       # FastAPI route handlers
│   │   ├── cv/        # Computer vision (MediaPipe, validation)
│   │   ├── geometry/  # Measurements, symmetry, ratios
│   │   ├── scoring/   # Scoring engine
│   │   ├── models/    # Pydantic models
│   │   ├── services/  # Orchestration layer
│   │   └── utils/     # Shared utilities
│   └── tests/         # Unit & integration tests
├── ml/                # ML experiments (post-V1)
├── docs/              # Documentation
└── docker-compose.yml
```

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Privacy

- Uploaded images are processed in memory and deleted immediately after analysis.
- No facial images are stored by default.
- No images are used for model training without explicit consent.

---

## License

MIT
