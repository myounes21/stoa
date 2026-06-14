# STOA

## Overview

STOA is a multi-agent adversarial debate framework. It leverages artificial intelligence to facilitate structured discourse on user-provided topics. Two autonomous AI teams argue opposing positions, and an independent, isolated judge panel evaluates the debate. By orchestrating multiple specialized agents (Strategist, Researcher, Critic, Speaker, Clerk, and Analyst), STOA aims to demonstrate how truth and clarity can emerge from structured, adversarial analysis rather than consensus.

## Key Features

- **Multi-Agent Orchestration:** Utilizes LangGraph to coordinate 11 specialized agent nodes executing across Groq and Gemini models.
- **Adversarial Debate Flow:** Two teams independently research, critique, and form arguments in parallel to construct robust cases.
- **Automated Fact-Checking:** A dedicated judge panel extracts claims, cross-references them via Tavily search, and penalizes inaccurate statements.
- **Real-Time Streaming:** Built with WebSockets to deliver low-latency streaming of agent outputs, debate progression, and final verdicts to the frontend.
- **Robust Error Handling:** Features a self-correcting Critic loop that evaluates internal strategies before finalizing arguments.

## Architecture

The system consists of two primary services:
- **Backend:** A FastAPI application orchestrating the agent graph via LangGraph, managing WebSockets, and integrating with external LLMs and search tools.
- **Frontend:** A React and Vite-based single-page application that provides a real-time interface for observing the debate and reading the judge's final verdict.

For a comprehensive breakdown of the agent definitions, state schema, and workflows, please refer to the [Architecture Documentation](docs/architecture.md).

## Technology Stack

- **Core:** Python, React, Vite, Tailwind CSS
- **AI & Orchestration:** LangGraph, LangChain, Groq API, Gemini API
- **External Integrations:** Tavily Search API
- **Backend:** FastAPI, Uvicorn, WebSockets
- **Package Management:** uv

## Setup and Installation

### Prerequisites

- Python 3.12+
- Node.js 18+
- API Keys for Groq, Google Gemini, and Tavily

### Local Development

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd STOA
   ```

2. **Backend Setup**
   Ensure `uv` is installed, then set up the Python environment:
   ```bash
   cd backend
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt # Or run uv sync if configured
   ```
   Create a `.env` file in the `backend` directory:
   ```env
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   FRONTEND_URL=http://localhost:5173
   ```
   Start the backend server:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```
   Create a `.env.local` file in the `frontend` directory:
   ```env
   VITE_WS_URL=ws://localhost:8000/ws/debate
   ```
   Start the frontend development server:
   ```bash
   npm run dev
   ```

## Deployment

### Backend (Railway)
- **Root Directory:** `/`
- **Start Command:** `uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT` (configured via `Procfile`)
- Ensure all environment variables (`GROQ_API_KEY`, `GOOGLE_API_KEY`, `TAVILY_API_KEY`, `FRONTEND_URL`) are provided in the Railway dashboard.
- `FRONTEND_URL` is used for HTTP CORS. Ensure the exact Vercel URL is used without a trailing slash.

### Frontend (Vercel)
- **Root Directory:** `frontend`
- Configure the `VITE_WS_URL` environment variable to point to your deployed backend WebSocket endpoint (e.g., `wss://your-railway-backend.up.railway.app/ws/debate`). Ensure the `/ws/debate` path is included.
