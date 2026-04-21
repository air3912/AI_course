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
