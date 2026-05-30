STOA/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dispatcher.py
│   │   ├── team/
│   │   │   ├── __init__.py
│   │   │   ├── strategist.py
│   │   │   ├── researcher.py
│   │   │   ├── critic.py
│   │   │   └── speaker.py
│   │   └── judges/
│   │       ├── __init__.py
│   │       ├── analyst.py
│   │       └── clerk.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── websocket.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── session.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── groq.py
│   │   └── gemini.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── state.py
│   ├── prompts/
│   │   ├── dispatcher.yaml
│   │   ├── teams.yaml
│   │   └── judges.yaml
│   ├── tools/
│   │   ├── __init__.py
│   │   └── search.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── prompts.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_critic.py
│   │   ├── test_dispatcher.py
│   │   ├── test_dispatcher_chat.py
│   │   ├── test_graph.py
│   │   ├── test_judges.py
│   │   ├── test_researcher.py
│   │   ├── test_retry_loop.py
│   │   ├── test_speaker.py
│   │   ├── test_strategist.py
│   │   ├── test_team.py
│   │   └── test_websocket.py
│   ├── .env
│   ├── .env.example
│   ├── config.py
│   └── main.py
├── docs/
│   ├── STOA_documentation.md
│   └── STOA_file_sturcture.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   │   ├── hero.png
│   │   │   ├── react.svg
│   │   │   └── vite.svg
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── README.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
├── notebooks/
│   └── test_llm.ipynb
├── stoa desing/
│   ├── stoa_debate_ui.html
│   └── stoa_verdict_panel.html
├── .gitignore
├── .python-version
├── .idea/
├── .venv/
├── Procfile
├── pyproject.toml
├── uv.lock
└── README.md
