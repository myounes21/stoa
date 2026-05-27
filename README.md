
# STOA

## Deployment

This repo is deployed as two services:

- Backend on Railway (FastAPI + WebSockets)
- Frontend on Vercel (Vite static build)

### Railway (backend)

Root directory: `/`

Start command (already in `Procfile`):

```
web: uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```
GROQ_API_KEY=...
GOOGLE_API_KEY=...
TAVILY_API_KEY=...
FRONTEND_URL=https://your-app.vercel.app
```

Notes:

- `FRONTEND_URL` is used for HTTP CORS. Use the exact Vercel URL without a trailing slash.

### Vercel (frontend)

Root directory: `frontend`

Environment variables:

```
VITE_WS_URL=wss://your-railway-backend.up.railway.app/ws/debate
```

Notes:

- `VITE_WS_URL` must include the `/ws/debate` path.

### Local dev

Create `frontend/.env.local`:

```
VITE_WS_URL=ws://localhost:8000/ws/debate
```
