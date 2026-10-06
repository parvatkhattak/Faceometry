# Faceometry Startup Guide

How to start, use, and stop Faceometry locally. The backend runs on port **8000** and the frontend on port **3000**.

## Prerequisites

- Python 3.10+
- Node.js 20+ and npm

## First-time setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

## Start the servers

Open two terminals from the project root.

**Terminal 1: backend**

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: frontend**

```bash
cd frontend
npm run dev -- --port 3000
```

## Verify

| Check | URL |
|-------|-----|
| App | http://localhost:3000 |
| Health | http://localhost:8000/health |
| API docs | http://localhost:8000/docs |

```bash
curl http://localhost:8000/health        # {"status":"healthy"}
```

## Using the app

1. Open http://localhost:3000 and click to start an analysis.
2. Upload a sharp, well-lit, front-facing photo with one face (JPG, PNG, or WebP, up to 10 MB).
3. Wait for the analysis steps to finish. You are taken to the results page.

## Run with Docker (backend only)

```bash
docker compose up --build
```

Run the frontend separately with `npm run dev`.

## Run tests

```bash
cd backend && source venv/bin/activate && pytest -v
cd ../frontend && npm run lint && npm run build
```

## Stop the servers

Press `Ctrl+C` in each terminal. If a port is still busy:

```bash
fuser -k 8000/tcp 3000/tcp
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `422 Image validation failed` | Use a sharper, front-facing, evenly lit photo with exactly one face. See the issues listed in the response. |
| CORS error in the browser | Add your frontend origin to `FACEOMETRY_CORS_ORIGINS`. |
| Frontend cannot reach the API | Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` and restart `npm run dev`. |
| `address already in use` | Stop the old process with the `fuser` command above. |
| MediaPipe or OpenCV import errors | Activate the venv and run `pip install -r requirements.txt` again. |

See [README.md](README.md) for configuration and API details.
