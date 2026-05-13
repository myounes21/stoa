STOA/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── websocket.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── session.py
│   │
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
│   │       ├── clerk.py
│   │       └── analyst.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── groq.py
│   │   └── gemini.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── state.py
│   │
│   ├── prompts/
│   │   ├── dispatcher.yaml
│   │   ├── teams.yaml
│   │   └── judges.yaml
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   └── search.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_dispatcher.py
│   │   ├── test_team.py
│   │   ├── test_graph.py
│   │   └── test_judges.py
│   │
│   ├── config.py
│   ├── main.py
│   └── .env
│
├── frontend/
│ 
│
├── docs/
│   └── STOA_documentation.md
│
├── .gitignore
├── pyproject.toml
└── README.md
