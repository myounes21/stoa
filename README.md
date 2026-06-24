# STOA

Welcome to STOA! This is a multi-agent debate framework I built to facilitate structured, adversarial discussions on any given topic. Instead of trying to find consensus right away, STOA pits two autonomous AI teams against each other to argue opposing positions. A separate, isolated judge panel then evaluates the whole debate. 

By having specialized agents (like a Strategist, Researcher, Critic, Speaker, Clerk, and Analyst) work together, the goal is to see if we can get to the truth through structured adversarial analysis.

## What's inside

- **LangGraph Orchestration:** I used LangGraph to coordinate 11 different agent nodes that run across Groq and Gemini models.
- **Adversarial Flow:** The two teams work in parallel to research, critique, and build their arguments independently.
- **Fact-Checking:** There's a dedicated judge panel that pulls out claims and checks them against the Tavily search API, penalizing anything that isn't accurate.
- **Real-Time UI:** Everything is streamed to the frontend via WebSockets, so you can watch the debate unfold live with super low latency.
- **Self-Correction:** The Critic agent constantly evaluates the team's internal strategy before any argument is actually spoken.

## Tech Stack

Here's what I used to build it:
- **Core:** Python, React, Vite, Tailwind CSS
- **AI stuff:** LangGraph, LangChain, Groq API, Gemini API
- **Search:** Tavily Search API
- **Backend:** FastAPI, Uvicorn, WebSockets
- **Package Manager:** uv

For more details on how the agents and state schemas work, check out the [Architecture Docs](docs/architecture.md).

## Getting Started

### Prerequisites
Make sure you have:
- Python 3.12+
- Node.js 18+
- API keys for Groq, Google Gemini, and Tavily

### Local Setup

1. **Clone the repo**
   ```bash
   git clone <repository_url>
   cd STOA
   ```

2. **Backend Setup**
   Make sure you have `uv` installed, then set up your environment:
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   uv pip install -r requirements.txt # Or run uv sync
   ```
   Create a `.env` file in the `backend` folder:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   FRONTEND_URL=http://localhost:5173
   ```
   Run the backend:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```
   Create a `.env.local` file in the `frontend` folder:
   ```env
   VITE_WS_URL=ws://localhost:8000/ws/debate
   ```
   Run the dev server:
   ```bash
   npm run dev
   ```

## Deployment

### Backend (Railway)
- I set it up to deploy from the root directory `/`.
- **Start Command:** `uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Don't forget to add your environment variables (`GROQ_API_KEY`, `GOOGLE_API_KEY`, `TAVILY_API_KEY`, `FRONTEND_URL`) in the Railway dashboard.
- Note: `FRONTEND_URL` is needed for CORS, so make sure it's the exact Vercel URL without a trailing slash.

### Frontend (Vercel)
- **Root Directory:** `frontend`
- Set the `VITE_WS_URL` to point to your deployed backend (e.g., `wss://your-railway-backend.up.railway.app/ws/debate`). Make sure to include the `/ws/debate` path.
