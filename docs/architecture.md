# STOA - Multi-Agent Adversarial Debate Framework
## Project Documentation

---

### 1. Project Overview

STOA is a multi-agent adversarial debate framework designed to orchestrate two autonomous AI teams arguing opposing positions on a given topic. An isolated judge panel subsequently evaluates the discourse. The framework operates on the foundational principle that structured, adversarial debate yields greater clarity and objective truth than consensus-driven models. 

---

### 2. Architectural Design

The system implements a multi-agent workflow coordinated via LangGraph:

```text
User Input
    │
    ▼
Dispatcher (Groq Model, Structured Output)
    ├── Requires Clarification ──► Stops execution (Prompts user for clarification)
    └── Valid Input ─────────────► Generates Arena Manifest
                                        │
    ┌───────────────────────────────────┴───────────────────────────────────┐
    ▼                                                                       ▼
Round 1 (Parallel Execution)
Team A Pipeline:                                                   Team B Pipeline:
Strategist ──► Researcher ──► Critic ──► Speaker                   Strategist ──► Researcher ──► Critic ──► Speaker
    │                                                                       │
    └───────────────────────────────────┬───────────────────────────────────┘
                                        ▼
                                  Collect Round
                   (Appends debate history, resets team states)
                                        │
                                        ▼
Round 2 (Parallel Execution)
(Strategist and Speaker utilize the updated debate history to formulate counter-arguments)
                                        │
                                        ▼
Judge Panel
    ├── Clerk: Extracts claims ──► Conducts Tavily searches ──► Verifies accuracy
    └── Analyst: Scores team performance ──► Issues final verdict
                                        │
                                        ▼
                        WebSocket Stream to Frontend Application
```

**Configuration Notes:**
- The default maximum number of debate rounds is set to 2. This is configured in `backend/config.py` and embedded within the Arena Manifest.
- The WebSocket initial state also establishes `max_rounds` to 2 in `backend/api/websocket.py`.

---

### 3. Agent Definitions

#### 3.1 Dispatcher
- **Model:** Groq model configured via `GROQ_LLM_MODEL` (default: `llama-3.3-70b-versatile`)
- **Tools:** None
- **Input:** Raw user query
- **Output:** `DispatcherOutput` (indicates if clarification is needed or provides the manifest)
- **Behavior:** Terminates the graph execution if the prompt is ambiguous, returning a `clarification_needed` signal.

#### 3.2 Strategist
- **Model:** Groq team model
- **Tools:** None
- **Input:** Arena manifest; additionally processes debate history during Round 2
- **Output:** `StrategyDocument` (JSON format)
- **Round 2 Objective:** Analyzes the opponent's previous argument to formulate a targeted rebuttal strategy.

#### 3.3 Researcher
- **Model:** Groq team model
- **Tools:** Tavily Search Engine (via `perform_research`)
- **Input:** `research_directives` from the Strategist, or a `retry_directive` if triggered by the Critic
- **Output:** `EvidenceDocument` (includes research summary, list of evidence, and tracking for failed searches)
- **Search Configuration:** `TAVILY_MAX_RESULTS` defaults to 2; operates with `search_depth="advanced"`.

#### 3.4 Critic
- **Model:** Groq team model
- **Tools:** None
- **Input:** Proposed Strategy and Evidence
- **Output:** `CriticDecision` (status, reasoning, identified weak points, and optional retry directives)
- **Retry Mechanism:** Permits a maximum of 2 rejections. The subsequent call forces an approval while flagging identified weaknesses for the Speaker.

#### 3.5 Speaker
- **Model:** Groq team model
- **Tools:** None
- **Input:** Strategy, Evidence, Critic's weak points, and the opponent's previous argument (in Round 2)
- **Output:** `SpeakerOutput` (the finalized argument text)

#### 3.6 Clerk (Judge)
- **Model:** Gemini model configured via `GEMINI_LLM_MODEL` (default: `gemini-2.5-flash`)
- **Tools:** Tavily Search Engine
- **Input:** Comprehensive debate transcript (derived from `debate_history`)
- **Output:** `TruthReport`
- **Execution Steps:** 
  1. Extracts factual claims from the transcript.
  2. Conducts independent searches for each claim.
  3. Verifies claims utilizing the transcript alongside aggregated search results.

#### 3.7 Analyst (Judge)
- **Model:** Gemini model configured via `GEMINI_LLM_MODEL`
- **Tools:** None
- **Input:** Debate transcript and the Clerk's `TruthReport`
- **Output:** `FinalVerdict`
- **Behavior:** Derives team designations from the manifest to provide a structured, written analysis and score.

---

### 4. LangGraph State Schema

The framework utilizes a typed dictionary to maintain state across the graph execution:

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

    # Team A Internal State
    team_a_strategy: Optional[str]
    team_a_evidence: Optional[str]
    team_a_critic_status: Optional[str]
    team_a_critic_decision: Optional[str]
    team_a_retry_count: int
    team_a_weakness_flag: bool
    team_a_argument: Optional[str]

    # Team B Internal State
    team_b_strategy: Optional[str]
    team_b_evidence: Optional[str]
    team_b_critic_status: Optional[str]
    team_b_critic_decision: Optional[str]
    team_b_retry_count: int
    team_b_weakness_flag: bool
    team_b_argument: Optional[str]

    # Debate History
    debate_history: list[dict]

    # Judge Panel Output
    truth_report: Optional[str]
    final_verdict: Optional[str]
    winner: Optional[str]
```

---

### 5. Data Models (Pydantic)

The system relies on Pydantic for rigorous data validation. Key schemas located in `backend/models/schemas.py` include:

- `DispatcherOutput`, `ArenaManifestLLM`, `ArenaManifest`
- `StrategyDocument`, `EvidenceItem`, `EvidenceDocument`
- `CriticDecision`, `SpeakerOutput`
- `ClaimsList`, `ClaimVerification`, `TruthReport`
- `TeamScores`, `FinalVerdict`

---

### 6. Execution Flow by Round

**Round 1:**
1. The Dispatcher initializes the Arena Manifest.
2. Team A and Team B execute asynchronously and in parallel through their respective pipelines: Strategist ──► Researcher ──► Critic ──► Speaker.
3. The `collect_round` process appends the generated arguments to the `debate_history`, resets the internal state for both teams, and increments the `current_round` counter.

**Round 2:**
1. Strategists receive the comprehensive `debate_history` along with the opponent's latest argument.
2. The teams execute the same pipeline as in Round 1, utilizing the new context for rebuttal.
3. Arguments are finalized and appended to the `debate_history`.

**Judge Phase:**
1. The Clerk extracts all factual claims, independently searches them via Tavily, verifies their validity, and compiles the `TruthReport`.
2. The Analyst reviews the transcript and the `TruthReport`, scores both teams, and generates the `FinalVerdict`.
3. Outcomes are streamed in real-time to the frontend application via WebSocket.

---

### 7. Core Engineering Decisions

- **Parallel Orchestration:** Implemented a fan-out/fan-in architecture to allow both teams to process rounds concurrently, significantly reducing latency.
- **Self-Correcting Loops:** The Critic agent operates on a retry loop with conditional routing, ensuring evidence standards are met before arguments are delivered. It defaults to a forced approval after two rejections to prevent infinite looping.
- **Targeted Rebuttals:** Round 2 is programmed with a "demolition" directive, compelling teams to directly address and dismantle the opponent's previous arguments.
- **Optimized Verification:** The Clerk extracts claims prior to initiating search queries to mitigate noise and ensure high relevance in search results. Parallelized Tavily searches are executed within a thread pool for optimal performance.
- **Real-Time Data Streaming:** Leveraged WebSocket streaming with `stream_mode="updates"` and a strictly typed message mapping protocol to deliver a responsive user interface.

---

### 8. Failure Mitigation

- Tavily search failures are isolated per query and returned as informational text to the Researcher agent to prevent complete pipeline halts.
- Groq API clients are configured with internal retry mechanisms (`max_retries=6`).
- Unhandled graph exceptions are intercepted and transmitted as standardized `error` messages via WebSocket.
- Requests requiring clarification safely terminate graph execution and prompt the user for refined input.

---

### 9. Technology Stack

- **Orchestration:** LangGraph
- **LLM Integration Framework:** LangChain
- **Team AI Models:** Groq (configured with `llama-3.3-70b-versatile`)
- **Judge AI Models:** Gemini (configured with `gemini-2.5-flash`)
- **Search Integration:** Tavily API
- **Backend Service:** FastAPI, Uvicorn
- **Real-Time Communication:** WebSockets
- **Frontend Interface:** React, Vite
- **Configuration Management:** `pydantic-settings`
- **Environment Management:** `uv`

---

### 10. Professional Impact & Achievements

- Engineered a multi-agent adversarial debate framework utilizing LangGraph to coordinate 11 specialized agent nodes across Groq and Gemini models.
- Designed and implemented a Critic-driven retry architecture that autonomously audits evidence and conditionally reroutes queries, ensuring robust argument formulation.
- Developed a claim extraction and verification pipeline integrating the Tavily Search API with Gemini scoring algorithms to identify and penalize factual inaccuracies.
- Optimized system latency by implementing a parallelized fan-out/fan-in orchestration model, enabling concurrent execution of team pipelines and search requests.
- Deployed a real-time, event-driven frontend architecture utilizing strictly typed WebSocket messages to stream agent outputs and judicial verdicts to a React application.
