# STOA Architecture Docs

Here's a breakdown of how STOA works under the hood. It's essentially a multi-agent debate system powered by LangGraph, where two AI teams argue against each other and a separate judge panel calls the winner.

---

### 1. High-Level Flow

The system runs a coordinated workflow using LangGraph:

```text
User Input
    │
    ▼
Dispatcher (Groq)
    ├── Needs Clarification ──► Stops execution and asks the user for details
    └── All Good ──────────────► Creates the Arena Manifest
                                      │
    ┌─────────────────────────────────┴─────────────────────────────────┐
    ▼                                                                   ▼
Round 1 (Parallel)
Team A Pipeline:                                               Team B Pipeline:
Strategist ──► Researcher ──► Critic ──► Speaker               Strategist ──► Researcher ──► Critic ──► Speaker
    │                                                                   │
    └─────────────────────────────────┬─────────────────────────────────┘
                                      ▼
                                Collect Round
                   (Saves history, resets team states)
                                      │
                                      ▼
Round 2 (Parallel)
(Strategist and Speaker look at the opponent's previous argument to plan rebuttals)
                                      │
                                      ▼
Judge Panel
    ├── Clerk: Extracts claims ──► Searches Tavily ──► Checks facts
    └── Analyst: Scores the teams ──► Writes the final verdict
                                      │
                                      ▼
                      WebSocket Stream to Frontend
```

*Note:* Right now, the maximum number of debate rounds is hardcoded to 2 in `backend/config.py` and the initial websocket state in `backend/api/websocket.py`. 

---

### 2. The Agents

#### Dispatcher
- **Model:** Groq (`GROQ_LLM_MODEL`, usually `llama-3.3-70b-versatile`)
- **What it does:** Looks at the raw user query. If it's too vague, it stops the graph and asks for clarification. If it's good, it generates the debate manifest.

#### Strategist
- **Model:** Groq
- **What it does:** Looks at the manifest (and debate history in Round 2) to build a JSON strategy for the team. In Round 2, its main job is figuring out how to tear down the opponent's argument.

#### Researcher
- **Model:** Groq
- **Tools:** Tavily Search Engine
- **What it does:** Takes the strategy (or a retry request from the Critic) and searches the web. It outputs an evidence document summarizing what it found. It uses `search_depth="advanced"` and grabs the top 2 results by default.

#### Critic
- **Model:** Groq
- **What it does:** The internal reviewer. It looks at the strategy and evidence and decides if it's good enough. If it's weak, it tells the Researcher to try again. It's capped at 2 rejections to prevent infinite loops.

#### Speaker
- **Model:** Groq
- **What it does:** Takes all the prep work (strategy, evidence, Critic notes, and opponent's argument) and writes the actual spoken argument.

#### Clerk (Judge Panel)
- **Model:** Gemini (`GEMINI_LLM_MODEL`, usually `gemini-2.5-flash`)
- **Tools:** Tavily Search Engine
- **What it does:** The fact-checker. It reads the whole transcript, pulls out factual claims, googles them independently, and creates a `TruthReport`.

#### Analyst (Judge Panel)
- **Model:** Gemini
- **What it does:** Reads the transcript and the Clerk's truth report to score the teams and write a final verdict.

---

### 3. State Schema

I'm using a typed dictionary to keep track of the state across the graph:

```python
class STOAState(TypedDict):
    # Setup
    user_query: str
    arena_manifest: Optional[dict]
    clarification_needed: Optional[bool]
    clarification_response: Optional[str]

    # Rounds
    current_round: int
    max_rounds: int

    # Team A State
    team_a_strategy: Optional[str]
    team_a_evidence: Optional[str]
    team_a_critic_status: Optional[str]
    team_a_critic_decision: Optional[str]
    team_a_retry_count: int
    team_a_weakness_flag: bool
    team_a_argument: Optional[str]

    # Team B State (same as Team A)
    team_b_strategy: Optional[str]
    # ...

    # History & Results
    debate_history: list[dict]
    truth_report: Optional[str]
    final_verdict: Optional[str]
    winner: Optional[str]
```

---

### 4. Data Models

Everything is strictly validated with Pydantic in `backend/models/schemas.py`. 
Key models: `DispatcherOutput`, `ArenaManifest`, `StrategyDocument`, `EvidenceDocument`, `CriticDecision`, `SpeakerOutput`, `TruthReport`, and `FinalVerdict`.

---

### 5. Design Decisions & Trade-offs

- **Parallel Execution:** Both teams run their pipelines concurrently using a fan-out/fan-in design. It saves a ton of time.
- **The Critic Loop:** I wanted teams to self-correct before speaking. The Critic handles this, but I hardcoded a max of 2 retries so it doesn't get stuck forever.
- **Fact-Checking Flow:** Doing RAG directly on a raw transcript is messy. Instead, the Clerk extracts claims *first*, then searches them individually. We run these Tavily searches in parallel threads.
- **WebSockets:** Since there's a lot going on, I set up a WebSocket connection that streams `updates` to the frontend so the UI feels alive.

### 6. Error Handling

- If Tavily fails, the error is passed back as text to the Researcher so the pipeline doesn't crash.
- Groq clients have built-in retries (`max_retries=6`).
- Unhandled graph errors get caught and streamed to the frontend as an `error` event.
