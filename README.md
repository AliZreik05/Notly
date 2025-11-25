# Notly — Transcription service

This repository contains the backend API for lecture transcription, summarization and history.

Quick start (recommended - Docker)

1. Copy .env.example to .env and optionally set OPENAI_API_KEY if you want real transcriptions and summaries:

```powershell
cp .env.example .env
# edit .env and add OPENAI_API_KEY
```

2. Start services (Redis, API, and worker):

```powershell
docker compose up --build
```

3. App will be available at http://localhost:8000

Notes
- The code uses ffprobe (from ffmpeg) to measure audio duration. The Docker image includes ffmpeg.
- If OPENAI_API_KEY is not set, the worker will create stub transcripts and summaries so the app still runs for development.
- The worker runs RQ queues and listens to the "transcriptions" queue.

API Endpoints
- POST /api/v1/transcriptions/upload — multipart form upload (user_id query param required). Fields: title, course_name (optional), file.
- GET /api/v1/transcriptions/history — query ?user_id and optional ?filter=today|week|month
- GET /api/v1/transcriptions/{id} — get detail (requires user_id)
- GET /api/v1/transcriptions/{id}/status — check status

If you need help wiring up your Android client or CI tests, tell me which part you want next and I will add tests or CI config.

Run tests

```powershell
pip install -r requirements.txt
pytest -q
```
