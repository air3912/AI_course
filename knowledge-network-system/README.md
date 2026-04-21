# Knowledge Network System

Analyze PDF/PPT files and build a knowledge relationship graph.

## Stack

- Backend: FastAPI (Python)
- Frontend: Vue 3 + Tailwind CSS + Vite

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r ..\requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: <http://localhost:5173>  
Backend default URL: <http://localhost:8000>

## Optional: Enable LLM Extraction (GPT/Qwen)

By default the backend uses a heuristic extractor (keywords/entities + co-occurrence edges).
You can optionally enable an LLM-based extractor via any OpenAI-compatible Chat Completions API.

1) Copy env template:

```bash
cp .env.example .env
```

2) Set in `.env`:

- `LLM_ENABLED=true`
- `LLM_BASE_URL` (e.g. `https://api.openai.com/v1` or your Qwen/OpenAI-compatible gateway)
- `LLM_API_KEY`
- `LLM_MODEL`

## Production Deployment (Docker)

This repository now includes a production Docker deployment set:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `docker-compose.prod.yml`

### 1) Prepare environment variables

Copy the production env template:

```bash
cp .env.prod.example .env
```

If you are on Windows PowerShell:

```powershell
Copy-Item .env.prod.example .env
```

Then edit `.env` and set at least:

- `CORS_ORIGINS` (your domain)

### 2) Build and start services

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

After startup:

- Frontend: `http://<your-server-ip>/`
- API health: `http://<your-server-ip>/api/v1/health`

### 3) Stop services

```bash
docker compose -f docker-compose.prod.yml down
```
