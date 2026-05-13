# STOA — Multi-Agent Adversarial Debate Framework
### Project Documentation & Implementation Roadmap

---

## 1. Project Overview

STOA is a multi-agent adversarial debate framework where two AI teams argue opposing positions on any topic, and an isolated judge panel evaluates the outcome. The name draws from the *Stoa Poikile* — the Athenian colonnade where philosophers argued and refined ideas through structured public discourse.

**Core principle:** Truth emerges from structured conflict, not consensus.

---

## 2. Final Architecture

```
User Input
    ↓
Dispatcher (clarifies if needed → max 1 exchange)
    ↓
Arena Manifest (JSON state object)
    ↓
Round 1 ──────────────────────────────────────────
    Team A (async) ──────── Team B (async)
    Strategist              Strategist
        ↓                       ↓
    Researcher (Tavily)     Researcher (Tavily)
        ↓                       ↓
    Critic (retry ≤2)       Critic (retry ≤2)
        ↓                       ↓
    Speaker                 Speaker
        ↓                       ↓
    Team A Output ────────── Team B Output
──────────────────────────────────────────────────
Round 2 (same flow, but Strategist reads full history)
──────────────────────────────────────────────────
    Judge Panel
    Clerk (Tavily) → Truth Report
    Analyst → Logic Scores + Final Verdict
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
→ Extracts: Team Python vs Team JavaScript
→ Fires immediately
```

**Path B — Ambiguous query:**
```
"What's the best anime?"
→ Asks: "I need two specific options. Which two are you choosing?"
→ User responds → fires
```

---

### 3.2 Strategist
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | None |
| Input | Arena Manifest + **full debate history** (Round 2 only) |
| Job | Define the win condition for this round. Identify strongest arguments for assigned position. Anticipate opponent's likely attacks. Produce a structured argument plan. |
| Output | Internal strategy document (key claims, attack angles, counter-anticipations) |
| Identity | Locked to assigned position. Cannot concede or acknowledge opponent's position as valid. |

**Note:** Round 1 — Strategist reads Arena Manifest only. Round 2 — Strategist reads full debate history to identify patterns and gaps in the opponent's case.

---

### 3.3 Researcher
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | Tavily Search (max 3 results per query) |
| Input | Strategist's argument plan |
| Job | Execute targeted web searches to ground the Strategist's plan in real evidence. Synthesize search results into structured evidence document. |
| Output | Evidence document (claims + real sources + supporting data) |
| Identity | Locked to assigned position. Only retrieves evidence that supports the team's case. |

**Failure handling:** If Tavily returns no results, Researcher flags it in output and Critic decides whether to retry with a different query or proceed with available context.

---

### 3.4 Critic
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | None |
| Input | Strategist's plan + Researcher's evidence document |
| Job | Audit the evidence. Check: Does evidence actually support the strategy? Are sources plausible? Are claims well-grounded or hallucinated? |
| Output | APPROVED or REJECTED with specific reason |
| Retry limit | Maximum 2 retries. After 2 rejections, automatically approves and passes to Speaker with a weakness flag. |

**Retry loop:**
```
Critic → REJECTED → Researcher retries (attempt 2)
Critic → REJECTED → Researcher retries (attempt 3)
Critic → REJECTED → Force APPROVED + weakness flag → Speaker
```

---

### 3.5 Speaker
| Property | Detail |
|---|---|
| Model | Llama-3.3-70B via Groq |
| Tool | None |
| Input | Strategist's plan + Critic-approved evidence + opponent's last argument (Round 2) |
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
| Job | Extract all factual claims made by both teams. Verify each claim against real sources. |
| Output | Truth Report (claim → verified/unverified/false + source) |
| Isolation | Has NO access to team strategies or internal deliberations. Reads transcript only. |

---

### 3.7 Analyst (Judge)
| Property | Detail |
|---|---|
| Model | Gemini 2.5 Pro |
| Tool | None |
| Input | Full debate transcript + Clerk's Truth Report |
| Job | Evaluate logical consistency, fallacy detection, rebuttal effectiveness, and argument quality. Penalize teams for hallucinated claims (from Truth Report). Produce final verdict. |
| Output | Logic scores per team + Winner declaration + Written analysis |
| Isolation | Has NO access to team strategies or internal deliberations. |

---

## 4. LangGraph State Schema

```python
class STOAState(TypedDict):
    # Arena Setup
    user_query: str
    arena_manifest: dict          # topic, logic_type, team_a_identity, team_b_identity
    clarification_needed: bool
    clarification_response: str

    # Round Tracking
    current_round: int            # 1 or 2
    max_rounds: int               # fixed at 2

    # Team A Internal (isolated from Judge)
    team_a_strategy: str
    team_a_evidence: str
    team_a_critic_status: str     # APPROVED / REJECTED
    team_a_retry_count: int       # max 2
    team_a_weakness_flag: bool
    team_a_argument: str          # Speaker output

    # Team B Internal (isolated from Judge)
    team_b_strategy: str
    team_b_evidence: str
    team_b_critic_status: str
    team_b_retry_count: int
    team_b_weakness_flag: bool
    team_b_argument: str

    # Debate History (visible to Strategist Round 2, Judge Panel)
    debate_history: list[dict]    # [{"round": 1, "team_a": "...", "team_b": "..."}]

    # Judge Panel (isolated — only receives debate_history)
    truth_report: str             # Clerk output
    final_verdict: str            # Analyst output
    winner: str                   # "Team A" / "Team B" / "Draw"
```

**State isolation rule:** Judge nodes receive `debate_history` only. They never receive `team_a_strategy`, `team_a_evidence`, `team_b_strategy`, or `team_b_evidence`. This is enforced at the node input level, not by convention.

---

## 5. Round Flow

### Round 1
1. Both teams receive Arena Manifest only
2. Team A and Team B run in parallel (asyncio)
3. Each team: Strategist → Researcher → Critic (retry if needed) → Speaker
4. Both Speakers produce Round 1 arguments
5. Arguments appended to `debate_history`

### Round 2
1. Both teams receive Arena Manifest + full `debate_history`
2. Same parallel flow
3. Strategist now reads full history — identifies opponent patterns, gaps, missed attacks
4. Same internal flow: Strategist → Researcher → Critic → Speaker
5. Round 2 arguments appended to `debate_history`

### Judge Phase
1. Clerk receives `debate_history` only → runs Tavily to verify claims → produces Truth Report
2. Analyst receives `debate_history` + Truth Report → scores + verdict
3. Final verdict streamed to frontend

---

## 6. Model & API Configuration

```python
# .env
GROQ_API_KEY=...
GOOGLE_API_KEY=...
TAVILY_API_KEY=...

# Models
TEAM_MODEL = "llama-3.3-70b-versatile"      # Groq
JUDGE_MODEL = "gemini-2.5-pro"              # Google

# Clients
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

team_llm = ChatGroq(model=TEAM_MODEL, temperature=0.7)
judge_llm = ChatGoogleGenerativeAI(model=JUDGE_MODEL, temperature=0.3)
```

**Why lower temperature for judges?** Evaluation tasks need consistency and precision. Generation tasks (Speaker) need some creativity and persuasive flair.

---

## 7. Key Engineering Decisions

### 7.1 Async Parallelization
Teams run concurrently using LangGraph's native async support. Neither team waits for the other. This halves the latency of each round.

```python
# LangGraph branch node
async def run_teams_parallel(state: STOAState):
    team_a_result, team_b_result = await asyncio.gather(
        run_team_a(state),
        run_team_b(state)
    )
    return {**team_a_result, **team_b_result}
```

### 7.2 Critic Retry Loop
Conditional edge in LangGraph — not a linear chain.

```python
def critic_router(state: STOAState) -> str:
    if state["team_a_critic_status"] == "APPROVED":
        return "speaker"
    if state["team_a_retry_count"] >= 2:
        return "speaker"          # force proceed with weakness flag
    return "researcher"           # loop back
```

### 7.3 Identity Locking
Every team agent receives this in their system prompt:

```
You are permanently assigned to argue FOR [position].
You CANNOT concede, agree with the opponent, or acknowledge
their position as valid under any circumstances.
Your only goal is to WIN this debate for [position].
```

### 7.4 State Isolation for Judges
Judge nodes are fed a filtered state:

```python
def build_judge_input(state: STOAState) -> dict:
    return {
        "debate_history": state["debate_history"]
        # Deliberately excludes all team internal fields
    }
```

### 7.5 Streaming
Each agent output streams to the frontend via WebSocket as it's produced — users watch the debate unfold in real time rather than waiting for a full round to complete.

---

## 8. Failure Handling

| Failure | Handling |
|---|---|
| Tavily returns no results | Researcher flags it, Critic decides whether to retry with different query or proceed |
| Critic rejects 2 times | Force approve, set `weakness_flag=True`, Speaker proceeds |
| Gemini API down | Return graceful error, surface to user, debate stops cleanly |
| LLM returns malformed output | Retry once with stricter output format instruction, then fail gracefully |

---

## 9. Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| LLM Framework | LangChain |
| Team Models | Llama-3.3-70B via Groq |
| Judge Models | Gemini 2.5 Pro via Google API |
| Search Tool | Tavily |
| Backend | FastAPI |
| Real-time | WebSockets |
| Frontend | React (simple dashboard) |
| Config | python-dotenv |
| Package Manager | uv |

---

## 10. Implementation Roadmap

### Phase 1 — Foundation
- [ ] Project setup (uv, FastAPI, env config)
- [ ] LangGraph state schema (`STOAState`)
- [ ] Dispatcher agent (prompt + clarification logic)
- [ ] Arena Manifest generation

### Phase 2 — Team Agents
- [ ] Strategist agent (prompt + identity locking)
- [ ] Researcher agent (Tavily tool integration)
- [ ] Critic agent (APPROVED/REJECTED output format)
- [ ] Critic retry loop (conditional edge in LangGraph)
- [ ] Speaker agent (character-locked persuasive output)
- [ ] Wire single team flow end-to-end (Team A only first)
- [ ] Test full Team A flow on one topic

### Phase 3 — Parallelization & Rounds
- [ ] Mirror Team A flow for Team B
- [ ] Async parallel execution of both teams
- [ ] Round tracking in state
- [ ] Debate history accumulation
- [ ] Round 2 — Strategist receives full debate history
- [ ] Test full 2-round debate flow

### Phase 4 — Judge Panel
- [ ] Clerk agent (Tavily + Gemini, state isolation)
- [ ] Analyst agent (Gemini, Truth Report input, verdict output)
- [ ] Verdict format design (scores + winner + analysis)
- [ ] Wire Judge Panel after Round 2

### Phase 5 — API & Streaming
- [ ] FastAPI endpoints
- [ ] WebSocket streaming of agent outputs
- [ ] Graceful failure handling across all agents

### Phase 6 — Frontend
- [ ] Single input box + clarification display
- [ ] Real-time debate stream view (agent outputs as they arrive)
- [ ] Final verdict display (scores, winner, analysis)

### Phase 7 — Polish
- [ ] End-to-end test with 3 different topic types
- [ ] Latency profiling (async working correctly?)
- [ ] README + architecture diagram
- [ ] CV bullets finalized

---

## 11. Verdict Format

```json
{
  "winner": "Team A",
  "scores": {
    "team_a": {
      "factual_accuracy": 8,
      "logical_consistency": 7,
      "rebuttal_effectiveness": 9,
      "overall": 8.0
    },
    "team_b": {
      "factual_accuracy": 5,
      "logical_consistency": 6,
      "rebuttal_effectiveness": 6,
      "overall": 5.7
    }
  },
  "truth_report_summary": "Team A made 4 verifiable claims, 3 confirmed. Team B made 5 claims, 2 confirmed, 1 false.",
  "written_analysis": "Team A consistently grounded their arguments in verified data...",
  "penalties": ["Team B: 1 hallucinated statistic detected in Round 1"]
}
```

---

## 12. CV Bullets

- **Engineered a multi-agent adversarial debate framework** using LangGraph with 10 specialized agents across a heterogeneous model stack (Llama-3.3-70B via Groq for execution, Gemini 2.5 Pro for evaluation)
- **Implemented a Reflexion-based self-correction pipeline** where Critic agents audit Researcher outputs and trigger conditional retry loops (max 2 retries) before any argument reaches the debate arena, reducing hallucination propagation
- **Architected a decoupled evaluation suite** where Judge agents operate on debate transcripts only — with zero visibility into team strategy — producing bias-mitigated verdicts via real-time fact-checking (Tavily) and multi-dimensional logic scoring
- **Optimized system throughput** by parallelizing adversarial team execution via asyncio, reducing per-round latency by ~50% compared to sequential orchestration
- **Designed a smart Dispatcher agent** performing autonomous task decomposition — extracting debate positions from natural language queries with a single-exchange clarification protocol before firing the arena
