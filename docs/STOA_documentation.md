# STOA - Multi-Agent Adversarial Debate Framework
### Project Documentation (Aligned to current implementation)

---

## 1. Project Overview

STOA is a multi-agent adversarial debate framework where two AI teams argue opposing positions on any topic, and an isolated judge panel evaluates the outcome. The name draws from the Stoa Poikile, the Athenian colonnade where philosophers argued and refined ideas through structured public discourse.

Core principle: Truth emerges from structured conflict, not consensus.

---

## 2. Current Architecture

```
User Input
    |
Dispatcher (Groq, structured output)
    |-- clarification_needed -> stop (client asks user to clarify)
    |-- Arena Manifest
    |
Round 1 (parallel)
    Team A: Strategist -> Researcher (Tavily) -> Critic -> Speaker
    Team B: Strategist -> Researcher (Tavily) -> Critic -> Speaker
    |
collect_round -> debate_history + reset team state
    |
Round 2 (parallel; Strategist + Speaker use debate history)
    |
Judge Panel
    Clerk: extract claims (Gemini) -> search each claim (Tavily) -> verify (Gemini)
    Analyst: score + verdict (Gemini)
    |
WebSocket stream -> frontend
```

Notes:
- Default max rounds is 2, configured in `backend/config.py` and embedded into the manifest.
- WebSocket initial state also sets `max_rounds` to 2 in `backend/api/websocket.py`.

---

## 3. Agent Definitions

### 3.1 Dispatcher
| Property | Detail |
|---|---|
| Model | Groq model from `GROQ_LLM_MODEL` (default: llama-3.3-70b-versatile) |
| Tool | None |
| Input | Raw user query |
| Output | `DispatcherOutput` (clarification or manifest) |
| Behavior | If unclear, returns `clarification_needed` and stops the graph. |

### 3.2 Strategist
| Property | Detail |
|---|---|
| Model | Groq team model (`GROQ_LLM_MODEL`) |
| Tool | None |
| Input | Arena manifest; debate history in Round 2 |
| Output | `StrategyDocument` JSON |
| Round 2 | Uses the opponent's last argument to build a demolition plan. |

### 3.3 Researcher
| Property | Detail |
|---|---|
| Model | Groq team model |
| Tool | Tavily search via `perform_research` |
| Input | Strategist `research_directives` (or `retry_directive` on retries) |
| Output | `EvidenceDocument` (summary, evidence_list, failed_searches) |
| Search config | `TAVILY_MAX_RESULTS` default 2, `search_depth="advanced"` |

### 3.4 Critic
| Property | Detail |
|---|---|
| Model | Groq team model |
| Tool | None |
| Input | Strategy + Evidence |
| Output | `CriticDecision` (status, reasoning, weak_points, retry_directive) |
| Retry limit | Up to 2 rejections; next Critic call force-approves with weakness flag. |

### 3.5 Speaker
| Property | Detail |
|---|---|
| Model | Groq team model |
| Tool | None |
| Input | Strategy, Evidence, Critic weak_points, opponent argument in Round 2 |
| Output | `SpeakerOutput` (argument text) |

### 3.6 Clerk (Judge)
| Property | Detail |
|---|---|
| Model | Gemini model from `GEMINI_LLM_MODEL` (default: gemini-2.5-flash) |
| Tool | Tavily search |
| Input | Full debate transcript (from `debate_history`) |
| Output | `TruthReport` |
| Steps | (1) Extract claims -> (2) Search each claim -> (3) Verify using transcript + search results |

Note: The verify step receives the transcript and aggregated search results. The extracted claim list is not passed to the verify step.

### 3.7 Analyst (Judge)
| Property | Detail |
|---|---|
| Model | Gemini model from `GEMINI_LLM_MODEL` |
| Tool | None |
| Input | Debate transcript + TruthReport |
| Output | `FinalVerdict` |
| Notes | Uses team names from the manifest for written analysis. |

---

## 4. LangGraph State Schema

```python
class STOAState(TypedDict):
    # Arena Setup
    user_query: str
    arena_manifest: Optional[dict]
    clarification_needed: Optional[bool]
    clarification_response: Optional[str]

    # Round Tracking
    current_round: int
    max_rounds: int

    # Team A Internal
    team_a_strategy: Optional[str]
    team_a_evidence: Optional[str]
    team_a_critic_status: Optional[str]
    team_a_critic_decision: Optional[str]
    team_a_retry_count: int
    team_a_weakness_flag: bool
    team_a_argument: Optional[str]

    # Team B Internal
    team_b_strategy: Optional[str]
    team_b_evidence: Optional[str]
    team_b_critic_status: Optional[str]
    team_b_critic_decision: Optional[str]
    team_b_retry_count: int
    team_b_weakness_flag: bool
    team_b_argument: Optional[str]

    # Debate History
    debate_history: list[dict]

    # Judge Panel
    truth_report: Optional[str]
    final_verdict: Optional[str]
    winner: Optional[str]
```

Debate history entries look like:

```json
{"round": 1, "team_a": "...", "team_b": "..."}
```

Judge nodes only read `debate_history` and `truth_report` (and the manifest for names). There is no explicit state slicing in the graph.

---

## 5. Pydantic Schemas (backend/models/schemas.py)

```python
class DispatcherOutput(BaseModel):
    clarification_needed: bool
    clarification_response: Optional[str]
    manifest: Optional[ArenaManifestLLM]

class ArenaManifestLLM(BaseModel):
    topic: str
    team_a: TeamMission
    team_b: TeamMission
    judicial_focus: List[str]

class ArenaManifest(ArenaManifestLLM):
    session_id: str
    max_rounds: int

class StrategyDocument(BaseModel):
    win_condition: str
    core_claims: List[str]
    anticipated_attacks: List[str]
    research_directives: List[str]

class EvidenceItem(BaseModel):
    claim: str
    source_url: Optional[str]
    extracted_fact: str

class EvidenceDocument(BaseModel):
    research_summary: str
    evidence_list: List[EvidenceItem]
    failed_searches: List[str]

class CriticDecision(BaseModel):
    status: Literal["APPROVED", "REJECTED"]
    reasoning: str
    weak_points: List[str]
    retry_directive: Optional[str]

class SpeakerOutput(BaseModel):
    argument: str

class ClaimsList(BaseModel):
    claims: list[str]

class ClaimVerification(BaseModel):
    claim: str
    team: str
    verdict: Literal["VERIFIED", "UNVERIFIED", "FALSE"]
    source_url: Optional[str]
    explanation: str

class TruthReport(BaseModel):
    verified_count: int
    unverified_count: int
    false_count: int
    claims: List[ClaimVerification]
    summary: str

class TeamScores(BaseModel):
    factual_accuracy: int
    logical_consistency: int
    rebuttal_effectiveness: int
    overall: float

class FinalVerdict(BaseModel):
    winner: str
    team_a_scores: TeamScores
    team_b_scores: TeamScores
    written_analysis: str
    penalties: list[str]
```

---

## 6. Round Flow

### Round 1
1. Dispatcher generates the Arena Manifest.
2. Team A and Team B run in parallel (fan-out): Strategist -> Researcher -> Critic -> Speaker.
3. `collect_round` appends arguments to `debate_history`, resets team state, increments `current_round`.

### Round 2
1. Strategists receive full `debate_history` and the last opponent argument.
2. Same team flow as Round 1.
3. Round 2 arguments are appended to `debate_history`.

### Judge Phase
1. Clerk extracts claims, searches each claim with Tavily, verifies claims, and writes the TruthReport.
2. Analyst scores both teams and returns the FinalVerdict.
3. Results are streamed to the frontend via WebSocket.

---

## 7. Model and API Configuration

```bash
# backend/.env
GROQ_API_KEY=...
GEMINI_API_KEY=...
TAVILY_API_KEY=...
FRONTEND_URL=https://your-frontend.app
```

```python
# backend/config.py
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"
GEMINI_LLM_MODEL = "gemini-2.5-flash"
MAX_ROUNDS = 2
TAVILY_MAX_RESULTS = 2
```

Frontend WebSocket URL:

```bash
# frontend/.env.local
VITE_WS_URL=ws://localhost:8000/ws/debate
```

---

## 8. WebSocket Protocol

Endpoint: `/ws/debate`

Client sends:

```json
{"query": "Python vs JavaScript"}
```

Message types emitted by the backend:
- `arena_ready`
- `clarification_needed`
- `agent_output` (Strategist, Researcher, Critic)
- `argument` (Speaker)
- `round_complete`
- `truth_report`
- `verdict`
- `complete`
- `error`

---

## 9. Key Engineering Decisions

- Fan-out/fan-in orchestration so both teams run in parallel per round.
- Critic retry loop with conditional routing and forced approval after two rejections.
- Round 2 "demolition" directive forces direct rebuttal of the opponent's last argument.
- Clerk claim extraction before search to avoid noisy, irrelevant results.
- Parallel Tavily searches with a thread pool for lower latency.
- WebSocket streaming via `stream_mode="updates"` and a typed message mapper.

---

## 10. Failure Handling

- Tavily search errors are captured per query and passed to the Researcher as text.
- Groq clients retry internally (`max_retries=6`).
- Any unhandled exception in the graph is sent as a WebSocket `error` message.
- Clarification requests end the graph and prompt the user for a new query.

---

## 11. Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM Framework | LangChain |
| Team Models | Groq (llama-3.3-70b-versatile, configurable) |
| Judge Models | Gemini (gemini-2.5-flash, configurable) |
| Search Tool | Tavily |
| Backend | FastAPI |
| Real-time | WebSockets |
| Frontend | React + Vite |
| Config | pydantic-settings |
| Package Manager | uv |

---

## 12. Implementation Status

### Phase 1 - Foundation
- [x] Project setup (uv, FastAPI, env config)
- [x] LangGraph state schema (STOAState)
- [x] Dispatcher agent (prompt + clarification logic)
- [x] Arena Manifest generation

### Phase 2 - Team Agents
- [x] Strategist agent (prompt + identity locking)
- [x] Researcher agent (Tavily integration)
- [x] Critic agent (APPROVED/REJECTED output format)
- [x] Critic retry loop (conditional edge in LangGraph)
- [x] Speaker agent (character-locked persuasive output)
- [x] Full Team A flow
- [x] Full Team B flow

### Phase 3 - Parallelization and Rounds
- [x] Async parallel execution of both teams (fan-out/fan-in)
- [x] Round tracking and debate history
- [x] Round 2 uses debate history

### Phase 4 - Judge Panel
- [x] Clerk agent (extract claims -> search -> verify)
- [x] Analyst agent (TruthReport input, FinalVerdict output)

### Phase 5 - API and Streaming
- [x] FastAPI health endpoint
- [x] WebSocket streaming of agent outputs
- [x] Typed message protocol for frontend
- [x] Graceful error handling in WebSocket layer

### Phase 6 - Frontend
- [x] Query input + clarification flow
- [x] Real-time debate stream view
- [x] Judge panel + verdict display

### Phase 7 - Polish
- [ ] End-to-end tests with multiple topic types
- [ ] Latency profiling and tuning
- [ ] Architecture diagram in README
- [ ] CV bullets finalized

---

## 13. Verdict Format

```json
{
  "winner": "Team A",
  "team_a_scores": {
    "factual_accuracy": 9,
    "logical_consistency": 9,
    "rebuttal_effectiveness": 8,
    "overall": 8.8
  },
  "team_b_scores": {
    "factual_accuracy": 5,
    "logical_consistency": 8,
    "rebuttal_effectiveness": 6,
    "overall": 6.4
  },
  "written_analysis": "Team A emerged as the clear winner due to its superior factual accuracy...",
  "penalties": [
    "Team B: -2 factual_accuracy - false claim in Round 2"
  ]
}
```

---

## 14. CV Bullets

- Engineered a multi-agent adversarial debate framework using LangGraph with 11 agent nodes across Groq and Gemini models.
- Implemented a Critic-driven retry loop that audits evidence and conditionally reroutes searches before allowing arguments to proceed.
- Built a claim extraction and verification pipeline that pairs Tavily search with Gemini scoring to penalize false claims.
- Parallelized team execution with fan-out/fan-in orchestration and parallel search to reduce round latency.
- Streamed real-time agent outputs and verdicts to a React frontend via typed WebSocket messages.
