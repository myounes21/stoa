# STOA — Multi-Agent Adversarial Debate Framework
### Project Documentation (Updated — Reflects Actual Implementation)

---

## 1. Project Overview

STOA is a multi-agent adversarial debate framework where two AI teams argue opposing positions on any topic, and an isolated judge panel evaluates the outcome. The name draws from the *Stoa Poikile* — the Athenian colonnade where philosophers argued and refined ideas through structured public discourse.

**Core principle:** Truth emerges from structured conflict, not consensus.

---

## 2. Final Architecture

```
User Input
    |
Dispatcher (clarifies if needed -> max 1 exchange)
    |
Arena Manifest (JSON state object)
    |
Round 1 --------------------------------------------------
    Team A (async) ----------- Team B (async)
    Strategist                  Strategist
        |                           |
    Researcher (Tavily)         Researcher (Tavily)
        |                           |
    Critic (retry <= 2)         Critic (retry <= 2)
        |                           |
    Speaker                     Speaker
        |                           |
    Team A Output -------------- Team B Output
----------------------------------------------------------
Round 2 (same flow, Strategist reads full history)
----------------------------------------------------------
    Judge Panel
    Clerk: Step 1 -> Extract Claims (Gemini)
           Step 2 -> Search Each Claim (Tavily)
           Step 3 -> Verify Claims -> Truth Report (Gemini)
    Analyst -> Logic Scores + Final Verdict (Gemini)
```

---

## 3. Agent Definitions

### 3.1 Dispatcher
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | None |
| Input | Raw user query |
| Job | Detect if query is clear enough to extract two positions. If yes, fire immediately. If ambiguous, ask one clarifying question. |
| Output | Arena Manifest JSON |
| Max exchanges | 1 clarifying question, then fires regardless |

**Path A — Clear query:**
```
"Is Python better than JavaScript for backend?"
-> Extracts: Team Python vs Team JavaScript
-> Fires immediately
```

**Path B — Ambiguous query:**
```
"What's the best anime?"
-> Asks: "I need two specific options. Which two are you choosing?"
-> User responds -> fires
```

---

### 3.2 Strategist
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | None |
| Input | Arena Manifest + full debate history (Round 2 only) |
| Job | Define the win condition for this round. Identify strongest arguments for assigned position. Anticipate opponent's likely attacks. Produce a structured argument plan with specific research directives. |
| Output | StrategyPlan (win_condition, core_claims, anticipated_attacks, research_directives) |
| Identity | Locked to assigned position. Cannot concede or acknowledge opponent's position as valid. |

**Note:** Round 1 — Strategist reads Arena Manifest only. Round 2 — Strategist reads full debate history to identify patterns and gaps in the opponent's case.

---

### 3.3 Researcher
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | Tavily Search (max 3 results per query, full page content) |
| Input | Strategist's research_directives |
| Job | Execute targeted web searches for each directive. Synthesize results into a structured evidence document. |
| Output | EvidenceDocument (list of evidence items: claim + source + supporting_data) |
| Identity | Locked to assigned position. Only retrieves evidence that supports the team's case. |

**Failure handling:** If Tavily returns no results for a directive, Researcher flags it. Critic decides whether to retry with a different query or proceed with available evidence.

---

### 3.4 Critic
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | None |
| Input | Strategist's StrategyPlan + Researcher's EvidenceDocument |
| Job | Audit the evidence. Does evidence actually support the strategy? Are sources plausible? Are claims well-grounded or hallucinated? |
| Output | CriticDecision (status: APPROVED or REJECTED, reason, retry_directive if rejected) |
| Retry limit | Maximum 2 retries. After 2 rejections, automatically approves with weakness flag. |

**Retry loop:**
```
Critic -> REJECTED -> Researcher retries (attempt 2)
Critic -> REJECTED -> Researcher retries (attempt 3)
Critic -> REJECTED -> Force APPROVED + weakness_flag=True -> Speaker
```

---

### 3.5 Speaker
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | None |
| Input | Strategist's plan + Critic-approved evidence + opponent's last argument (Round 2 only) |
| Job | Synthesize vetted research into a persuasive, confident, character-locked public argument. |
| Output | Final argument text (the public-facing debate output) |
| Identity | Fully locked to assigned position. Aggressive, persuasive tone. No hedging. |

---

### 3.6 Clerk (Judge)
| Property | Detail |
|---|---|
| Model | Gemini 2.5 Pro |
| Tool | Tavily Search |
| Input | Full debate transcript (both teams, both rounds) |
| Job | Two-step process: (1) Extract specific verifiable factual claims from transcript. (2) Search each claim individually. (3) Verify each claim against search results. |
| Output | TruthReport (verified_count, false_count, unverified_count, claim_verifications list) |
| Isolation | Has NO access to team strategies or internal deliberations. Reads transcript only. |

**Why two steps?** The original single-step design sent raw argument text as search queries, producing irrelevant results and inconsistent verification counts. The two-step approach extracts specific claims first, then searches for each one directly — producing targeted, reliable results.

---

### 3.7 Analyst (Judge)
| Property | Detail |
|---|---|
| Model | Gemini 2.5 Pro |
| Tool | None |
| Input | Full debate transcript + Clerk's TruthReport |
| Job | Evaluate logical consistency, fallacy detection, rebuttal effectiveness, and argument quality. Penalize teams for false claims. Produce final verdict. |
| Output | FinalVerdict (winner, team_a_scores, team_b_scores, written_analysis, penalties) |
| Isolation | Has NO access to team strategies or internal deliberations. |

---

## 4. LangGraph State Schema

```python
class STOAState(TypedDict):
    # Arena Setup
    user_query: str
    arena_manifest: dict
    clarification_needed: bool
    clarification_response: str

    # Round Tracking
    current_round: int            # 1 or 2
    max_rounds: int               # fixed at 2

    # Team A Internal (isolated from Judge)
    team_a_strategy: str
    team_a_evidence: str
    team_a_critic_status: str     # APPROVED / REJECTED
    team_a_critic_decision: str   # full CriticDecision JSON
    team_a_retry_count: int       # max 2
    team_a_weakness_flag: bool
    team_a_argument: str          # Speaker output

    # Team B Internal (isolated from Judge)
    team_b_strategy: str
    team_b_evidence: str
    team_b_critic_status: str
    team_b_critic_decision: str   # full CriticDecision JSON
    team_b_retry_count: int
    team_b_weakness_flag: bool
    team_b_argument: str

    # Debate History (visible to Strategist Round 2 and Judge Panel)
    debate_history: list[dict]    # [{"round": 1, "team_a": "...", "team_b": "..."}]

    # Judge Panel (isolated — only receives debate_history)
    truth_report: str             # Clerk TruthReport JSON
    final_verdict: str            # Analyst FinalVerdict JSON
    winner: str                   # "Team A" / "Team B" / "Draw"
```

**State isolation rule:** Judge nodes receive `debate_history` only. They never receive any `team_*_strategy`, `team_*_evidence`, or `team_*_critic_*` fields. Enforced at the node input level.

---

## 5. Pydantic Schemas

```python
# Dispatcher output
class ArenaManifest(BaseModel):
    topic: str
    team_a: dict                  # team_name, stance, mission_goal
    team_b: dict
    judicial_focus: list[str]
    session_id: str
    max_rounds: int

# Strategist output
class StrategyPlan(BaseModel):
    win_condition: str
    core_claims: list[str]
    anticipated_attacks: list[str]
    research_directives: list[str]

# Researcher output
class EvidenceItem(BaseModel):
    claim: str
    source: str
    supporting_data: str

class EvidenceDocument(BaseModel):
    evidence: list[EvidenceItem]
    search_gaps: list[str]        # directives that returned no results

# Critic output
class CriticDecision(BaseModel):
    status: str                   # "APPROVED" or "REJECTED"
    reason: str
    retry_directive: str          # populated only on REJECTED

# Clerk intermediate output (claim extraction step)
class ClaimsList(BaseModel):
    claims: list[str]

# Clerk final output
class ClaimVerification(BaseModel):
    claim: str
    team: str                     # "Team A" or "Team B"
    status: str                   # "VERIFIED", "FALSE", "UNVERIFIED"
    source: str
    explanation: str

class TruthReport(BaseModel):
    verified_count: int
    false_count: int
    unverified_count: int
    claim_verifications: list[ClaimVerification]

# Analyst output
class TeamScores(BaseModel):
    factual_accuracy: int
    logical_consistency: int
    rebuttal_effectiveness: int
    overall: float

class FinalVerdict(BaseModel):
    winner: str                   # "Team A" / "Team B" / "Draw"
    team_a_scores: TeamScores
    team_b_scores: TeamScores
    written_analysis: str
    penalties: list[str]
```

---

## 6. Round Flow

### Round 1
1. Both teams receive Arena Manifest only
2. Team A and Team B run in parallel (asyncio via LangGraph fan-out)
3. Each team: Strategist -> Researcher -> Critic (retry if needed) -> Speaker
4. Both Speakers produce Round 1 arguments
5. `collect_round` fan-in node appends arguments to `debate_history`, resets team state, increments round counter

### Round 2
1. Both teams receive Arena Manifest + full `debate_history`
2. Same parallel flow
3. Strategist reads full history — identifies opponent patterns, gaps, missed attacks
4. Round 2 arguments appended to `debate_history`

### Judge Phase
1. Clerk receives `debate_history` only
   - Step 1: Gemini extracts specific factual claims from transcript
   - Step 2: Tavily searches each claim individually
   - Step 3: Gemini verifies each claim against search results -> TruthReport
2. Analyst receives `debate_history` + TruthReport -> scores + verdict
3. Final verdict streamed to frontend via WebSocket

---

## 7. Model & API Configuration

```python
# .env
GROQ_API_KEY=...
GOOGLE_API_KEY=...
TAVILY_API_KEY=...

# Models
TEAM_MODEL = "llama-3.3-70b-versatile"
JUDGE_MODEL = "gemini-2.5-pro"

# Clients
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

team_llm = ChatGroq(model=TEAM_MODEL, temperature=0.7)
judge_llm = ChatGoogleGenerativeAI(model=JUDGE_MODEL, temperature=0.3)
```

**Why lower temperature for judges?** Evaluation tasks need consistency and precision. Generation tasks (Speaker) benefit from creative persuasive flair.

---

## 8. Key Engineering Decisions

### 8.1 Async Parallelization
Teams run concurrently using LangGraph's native fan-out/fan-in pattern. Neither team waits for the other. This halves the latency of each round.

```python
# dispatcher_router fans out to both teams simultaneously
def dispatcher_router(state: STOAState) -> list[str]:
    if state["clarification_needed"]:
        return [END]
    return ["strategist_a", "strategist_b"]

# collect_round is the fan-in node — LangGraph waits for both speakers
graph.add_edge("speaker_a", "collect_round")
graph.add_edge("speaker_b", "collect_round")
```

### 8.2 Critic Retry Loop
Conditional edge in LangGraph — not a linear chain. The router checks both approval status and retry count.

```python
def critic_router_a(state: STOAState) -> str:
    if state["team_a_critic_status"] == "APPROVED":
        return "speaker_a"
    if state["team_a_retry_count"] >= 2:
        return "speaker_a"        # force proceed with weakness flag
    return "researcher_a"         # loop back
```

### 8.3 Identity Locking
Every team agent receives this in their system prompt:

```
You are permanently assigned to argue FOR [position].
You CANNOT concede, agree with the opponent, or acknowledge
their position as valid under any circumstances.
Your only goal is to WIN this debate for [position].
```

### 8.4 State Isolation for Judges
Judge nodes are fed a filtered state slice:

```python
def build_judge_input(state: STOAState) -> dict:
    return {
        "debate_history": state["debate_history"]
        # Deliberately excludes all team_* internal fields
    }
```

### 8.5 Two-Step Clerk Verification
The Clerk uses two separate LLM calls to ensure accurate fact-checking:

- **Step 1 (extract_chain):** Gemini reads the full transcript and returns a `ClaimsList` — specific, searchable factual claims only. Opinions and vague assertions are excluded.
- **Step 2 (verify_chain):** Each claim is searched individually via Tavily. Gemini then verifies each claim against the targeted search results.

This replaced the original single-step design where raw argument text was sent as search queries — which produced irrelevant results and wildly inconsistent verification counts across runs.

### 8.6 WebSocket Streaming
Each agent output is streamed to the frontend via WebSocket as it's produced. LangGraph's `astream` with `stream_mode="updates"` emits node outputs one at a time. A `_format_node_update` mapper converts raw node output into typed frontend messages.

**Message types emitted:**
- `arena_ready` — topic and team names
- `argument` — team argument text (streamed per speaker)
- `round_complete` — round number
- `truth_report` — verification counts
- `verdict` — full scores, analysis, penalties, winner
- `complete` — debate finished
- `error` — any failure

---

## 9. Failure Handling

| Failure | Handling |
|---|---|
| Tavily returns no results | Researcher flags in search_gaps, Critic decides whether to retry or proceed |
| Critic rejects 2 times | Force approve, set weakness_flag=True, Speaker proceeds |
| Gemini API down | Graceful error returned, surfaced to frontend via error message type |
| LLM returns malformed output | Retry once with stricter format instruction, then fail gracefully |
| WebSocket disconnect | Caught via WebSocketDisconnect, no crash |

---

## 10. Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM Framework | LangChain |
| Team Models | Llama-3.3-70B via Groq |
| Judge Models | Gemini 2.5 Pro via Google API |
| Search Tool | Tavily |
| Backend | FastAPI |
| Real-time | WebSockets |
| Frontend | React (Phase 6) |
| Config | python-dotenv |
| Package Manager | uv |

---

## 11. Implementation Roadmap

### Phase 1 — Foundation
- [x] Project setup (uv, FastAPI, env config)
- [x] LangGraph state schema (STOAState)
- [x] Dispatcher agent (prompt + clarification logic)
- [x] Arena Manifest generation

### Phase 2 — Team Agents
- [x] Strategist agent (prompt + identity locking)
- [x] Researcher agent (Tavily tool integration)
- [x] Critic agent (APPROVED/REJECTED output format)
- [x] Critic retry loop (conditional edge in LangGraph)
- [x] Speaker agent (character-locked persuasive output)
- [x] Wire single team flow end-to-end (Team A only first)
- [x] Test full Team A flow on one topic

### Phase 3 — Parallelization & Rounds
- [x] Mirror Team A flow for Team B
- [x] Async parallel execution of both teams (LangGraph fan-out/fan-in)
- [x] Round tracking in state
- [x] Debate history accumulation
- [x] Round 2 — Strategist receives full debate history
- [x] Test full 2-round debate flow

### Phase 4 — Judge Panel
- [x] Clerk agent — two-step: extract claims + targeted Tavily search + Gemini verify
- [x] Analyst agent (Gemini, TruthReport input, FinalVerdict output)
- [x] Verdict format design (TeamScores + FinalVerdict schemas)
- [x] Wire Judge Panel after Round 2

### Phase 5 — API & Streaming
- [x] FastAPI endpoints (health check)
- [x] WebSocket streaming of agent outputs (stream_mode="updates")
- [x] Typed message protocol (arena_ready, argument, round_complete, truth_report, verdict, complete, error)
- [x] Graceful failure handling across all agents

### Phase 6 — Frontend
- [ ] Single input box + clarification display
- [ ] Real-time debate stream view (agent outputs as they arrive)
- [ ] Final verdict display (scores, winner, analysis, penalties)

### Phase 7 — Polish
- [ ] End-to-end test with 3 different topic types
- [ ] Latency profiling (async working correctly?)
- [ ] README + architecture diagram
- [ ] CV bullets finalized

---

## 12. Verdict Format

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
    "Team B: -2 factual_accuracy — falsely claimed X in Round 2"
  ]
}
```

---

## 13. CV Bullets

- **Engineered a multi-agent adversarial debate framework** using LangGraph with 10 specialized agents across a heterogeneous model stack (Llama-3.3-70B via Groq for execution, Gemini 2.5 Pro for evaluation)
- **Implemented a Reflexion-based self-correction pipeline** where Critic agents audit Researcher outputs and trigger conditional retry loops (max 2 retries) before any argument reaches the debate arena, reducing hallucination propagation
- **Architected a decoupled evaluation suite** where Judge agents operate on debate transcripts only — with zero visibility into team strategy — producing bias-mitigated verdicts via real-time fact-checking (Tavily) and multi-dimensional logic scoring
- **Designed a two-step claim verification pipeline** in the Clerk agent: an extraction pass isolates specific verifiable claims from debate transcripts before targeted web searches are executed per-claim, eliminating the inconsistent verification counts produced by naive full-text search queries
- **Optimized system throughput** by parallelizing adversarial team execution via LangGraph fan-out/fan-in, reducing per-round latency by approximately 50% compared to sequential orchestration
- **Designed a smart Dispatcher agent** performing autonomous task decomposition — extracting debate positions from natural language queries with a single-exchange clarification protocol before firing the arena
