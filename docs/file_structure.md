# STOA File Structure

This document outlines the directory and file organization for the STOA framework.

```text
STOA/
├── backend/                  # Core FastAPI application and LangGraph orchestration
│   ├── agents/               # AI agent implementations
│   │   ├── base.py
│   │   ├── dispatcher.py
│   │   ├── team/             # Team-specific agents (Strategist, Researcher, Critic, Speaker)
│   │   │   ├── strategist.py
│   │   │   ├── researcher.py
│   │   │   ├── critic.py
│   │   │   └── speaker.py
│   │   └── judges/           # Judge-specific agents (Clerk, Analyst)
│   │       ├── analyst.py
│   │       └── clerk.py
│   ├── api/                  # API endpoints and WebSocket handlers
│   │   ├── routes.py
│   │   └── websocket.py
│   ├── core/                 # LangGraph definitions and session management
│   │   ├── graph.py
│   │   └── session.py
│   ├── llm/                  # Language model integrations (Groq, Gemini)
│   │   ├── groq.py
│   │   └── gemini.py
│   ├── models/               # Pydantic schemas and state definitions
│   │   ├── schemas.py
│   │   └── state.py
│   ├── prompts/              # System prompts for all agents
│   │   ├── dispatcher.yaml
│   │   ├── teams.yaml
│   │   └── judges.yaml
│   ├── tools/                # External tool integrations
│   │   └── search.py         # Tavily search integration
│   ├── utils/                # Logging and utility functions
│   │   ├── logger.py
│   │   └── prompts.py
│   ├── tests/                # Test suite for agents and core logic
│   │   ├── test_critic.py
│   │   ├── test_dispatcher.py
│   │   ├── test_graph.py
│   │   ├── test_judges.py
│   │   ├── test_team.py
│   │   └── test_websocket.py
│   ├── config.py             # Application configuration and environment loading
│   └── main.py               # Application entry point
├── docs/                     # Project documentation
│   ├── architecture.md
│   └── file_structure.md
├── frontend/                 # React and Vite frontend application
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md                 # Primary entry point documentation
```
