import { Fragment, useEffect, useMemo, useRef, useState, useCallback } from "react";

const WS_URL = "ws://localhost:8001/ws/debate";

const AGENTS = ["Strategist", "Researcher", "Critic", "Speaker"];

const STATUS = {
  IDLE: "idle",
  ACTIVE: "active",
  APPROVED: "approved",
  REJECTED: "rejected",
  COMPLETE: "complete",
};

const STATUS_LABEL = {
  [STATUS.IDLE]: "Standby",
  [STATUS.ACTIVE]: "Active",
  [STATUS.APPROVED]: "Approved",
  [STATUS.REJECTED]: "Rejected",
  [STATUS.COMPLETE]: "Complete",
};

const SEED_QUESTIONS = [
  "Barcelona vs Real Madrid",
  "One Piece vs Attack on Titan",
  "Democracy vs Monarchy",
  "iOS vs Android",
  "Marvel vs DC",
  "React vs Vue",
];

const AGENT_ICONS = {
  Strategist: "S",
  Researcher: "R",
  Critic: "C",
  Speaker: "Sp",
};

const toArray = (value) => (Array.isArray(value) ? value : []);



function useDebate() {
  const [phase, setPhase] = useState("input");
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("");
  const [teams, setTeams] = useState({ A: "", B: "" });
  const [stances, setStances] = useState({ A: "", B: "" });
  const [missionGoals, setMissionGoals] = useState({ A: "", B: "" });
  const [judicialFocus, setJudicialFocus] = useState([]);
  const [round, setRound] = useState(1);
  const roundRef = useRef(1);
  const [agentStates, setAgentStates] = useState({
    A: { Strategist: STATUS.IDLE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
    B: { Strategist: STATUS.IDLE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
  });
  const [agentOutputs, setAgentOutputs] = useState({ A: {}, B: {} });
  const [agentHistory, setAgentHistory] = useState({ A: [], B: [] });
  const [, setArguments] = useState({ A: [], B: [] });
  const [truthReport, setTruthReport] = useState(null);
  const [verdict, setVerdict] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [lastUpdate, setLastUpdate] = useState(null);
  const [clarificationMessage, setClarificationMessage] = useState("");
  const [originalQuery, setOriginalQuery] = useState("");
  const [roundBanner, setRoundBanner] = useState(null);
  const wsRef = useRef(null);

  const setAgentStatus = useCallback((team, agent, statusValue) => {
    setAgentStates(prev => ({
      ...prev,
      [team]: { ...prev[team], [agent]: statusValue }
    }));
  }, []);

  const setAgentOutput = useCallback((team, agent, content) => {
    setAgentOutputs(prev => ({
      ...prev,
      [team]: { ...prev[team], [agent]: content }
    }));
  }, []);

  const appendAgentHistory = useCallback((team, agent, content, roundIndex) => {
    setAgentHistory(prev => ({
      ...prev,
      [team]: [...prev[team], { agent, content, round: roundIndex }]
    }));
  }, []);

  const startDebate = useCallback(() => {
    if (!query.trim()) return;

    setPhase("submitting");
    setStatus("Connecting to arena...");
    setError("");
    setClarificationMessage("");
    setVerdict(null);
    setTruthReport(null);
    setArguments({ A: [], B: [] });
    setAgentOutputs({ A: {}, B: {} });
    setAgentHistory({ A: [], B: [] });
    setLastUpdate(null);
    setAgentStates({
      A: { Strategist: STATUS.IDLE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
      B: { Strategist: STATUS.IDLE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
    });
    setRound(1);
    roundRef.current = 1;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ query }));
      setStatus("Debate in progress...");
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "arena_ready") {
        setPhase("debate");
        setTopic(msg.data.topic);
        setTeams({ A: msg.data.team_a, B: msg.data.team_b });
        setStances({ A: msg.data.team_a_stance, B: msg.data.team_b_stance });
        setMissionGoals({ A: msg.data.team_a_goal, B: msg.data.team_b_goal });
        setJudicialFocus(toArray(msg.data.judicial_focus));
        setStatus("Arena locked. Agents deploying...");
        setAgentStates({
          A: { Strategist: STATUS.ACTIVE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
          B: { Strategist: STATUS.ACTIVE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
        });
      }

      if (msg.type === "agent_output") {
        const { team, agent, content, status: agentStatus } = msg.data;

        let parsed = content;
        try { parsed = JSON.parse(content); } catch { /* keep raw string */ }

        setAgentOutput(team, agent, parsed);
        appendAgentHistory(team, agent, parsed, roundRef.current);
        setLastUpdate({ team, agent, round: roundRef.current });

        const criticDecision = parsed?.status || agentStatus;
        if (agent === "Critic") {
          if (criticDecision === "REJECTED") {
            setAgentStatus(team, agent, STATUS.REJECTED);
            setStatus(`Team ${team} Critic rejected evidence - retrying...`);
          } else {
            setAgentStatus(team, agent, STATUS.APPROVED);
          }
        } else {
          setAgentStatus(team, agent, STATUS.COMPLETE);
        }

        const idx = AGENTS.indexOf(agent);
        if (idx < AGENTS.length - 1 && agent !== "Critic") {
          setAgentStatus(team, AGENTS[idx + 1], STATUS.ACTIVE);
        }
        if (agent === "Strategist") setAgentStatus(team, "Researcher", STATUS.ACTIVE);
        if (agent === "Researcher") setAgentStatus(team, "Critic", STATUS.ACTIVE);
        if (criticDecision === "APPROVED") setAgentStatus(team, "Speaker", STATUS.ACTIVE);
      }

      if (msg.type === "argument") {
        const { team, content } = msg.data;
        setArguments(prev => ({
          ...prev,
          [team]: [...prev[team], { round: roundRef.current, content }]
        }));
        setAgentOutput(team, "Speaker", { argument: content });
        appendAgentHistory(team, "Speaker", { argument: content }, roundRef.current);
        setLastUpdate({ team, agent: "Speaker", round: roundRef.current });
        setAgentStatus(team, "Speaker", STATUS.COMPLETE);
        setStatus(`Team ${team} argument delivered.`);
      }

      if (msg.type === "round_complete") {
        setRound(r => {
          const nextRound = r + 1;
          roundRef.current = nextRound;
          return nextRound;
        });
        setStatus(`Round ${msg.data.round} complete. Round ${msg.data.round + 1} beginning...`);
        setAgentStates({
          A: { Strategist: STATUS.ACTIVE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
          B: { Strategist: STATUS.ACTIVE, Researcher: STATUS.IDLE, Critic: STATUS.IDLE, Speaker: STATUS.IDLE },
        });
        setRoundBanner({ from: msg.data.round, to: msg.data.round + 1 });
        setTimeout(() => setRoundBanner(null), 2500);
      }

      if (msg.type === "truth_report") {
        setTruthReport(msg.data);
        setStatus("Judges deliberating...");
      }

      if (msg.type === "verdict") {
        setVerdict(msg.data);
        setPhase("verdict");
        setStatus("Debate complete.");
      }

      if (msg.type === "clarification_needed") {
        setClarificationMessage(msg.data?.message || "Please provide two specific options to debate.");
        setOriginalQuery(msg.data?.original_query || query);
        setPhase("clarification");
        setStatus("Clarification needed.");
        ws.close();
      }

      if (msg.type === "complete") {
        setStatus("Debate complete.");
      }

      if (msg.type === "error") {
        setError(msg.message);
        setStatus("Error occurred.");
      }
    };

    ws.onerror = () => setError("WebSocket connection failed.");
    ws.onclose = () => {};
  }, [appendAgentHistory, query, setAgentOutput, setAgentStatus]);

  return {
    phase,
    query,
    setQuery,
    topic,
    teams,
    stances,
    missionGoals,
    judicialFocus,
    round,
    agentStates,
    agentOutputs,
    agentHistory,
    verdict,
    truthReport,
    lastUpdate,
    status,
    error,
    clarificationMessage,
    originalQuery,
    roundBanner,
    startDebate
  };
}

function StatusDot({ status }) {
  const dotClass = {
    [STATUS.IDLE]: "idle",
    [STATUS.ACTIVE]: "running",
    [STATUS.APPROVED]: "done",
    [STATUS.REJECTED]: "rejected",
    [STATUS.COMPLETE]: "done",
  };

  return <span className={`status-dot ${dotClass[status] || "idle"}`} />;
}

function AgentOutput({ agent, output }) {
  if (!output) {
    return <div className="output-text muted">Awaiting {agent.toLowerCase()} output.</div>;
  }

  if (typeof output === "string") {
    return <div className="output-text">{output}</div>;
  }

  if (agent === "Strategist") {
    const coreClaims = toArray(output.core_claims);
    const anticipatedAttacks = toArray(output.anticipated_attacks);
    const researchDirectives = toArray(output.research_directives);
    return (
      <div className="output-block">
        <div className="output-row">
          <span className="output-label">Win Condition</span>
          <span className="output-text">{output.win_condition}</span>
        </div>
        <details open className="output-details">
          <summary>Core Claims ({coreClaims.length})</summary>
          <div className="output-list">
            <ul>
              {coreClaims.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </details>
        <details open className="output-details">
          <summary>Anticipated Attacks ({anticipatedAttacks.length})</summary>
          <div className="output-list">
            <ul>
              {anticipatedAttacks.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </details>
        <details open className="output-details">
          <summary>Research Directives ({researchDirectives.length})</summary>
          <div className="output-list">
            <ul>
              {researchDirectives.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </details>
      </div>
    );
  }

  if (agent === "Researcher") {
    const evidenceList = toArray(output.evidence_list);
    const failedSearches = toArray(output.failed_searches);
    return (
      <div className="output-block">
        <div className="output-row">
          <span className="output-label">Summary</span>
          <span className="output-text">{output.research_summary}</span>
        </div>
        <details open className="output-details">
          <summary>Evidence ({evidenceList.length})</summary>
          <div className="output-list">
            <ul>
              {evidenceList.map((item, i) => (
                <li key={i}>
                  <strong>{item.claim}</strong>
                  <div className="output-sub">{item.extracted_fact}</div>
                  {item.source_url && (
                    <a className="output-link" href={item.source_url} target="_blank" rel="noreferrer">
                      Source
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </details>
        {failedSearches.length > 0 && (
          <details open className="output-details">
            <summary>Failed Searches ({failedSearches.length})</summary>
            <div className="output-list">
              <ul>
                {failedSearches.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          </details>
        )}
      </div>
    );
  }

  if (agent === "Critic") {
    const weakPoints = toArray(output.weak_points);
    return (
      <div className="output-block">
        <div className="output-row">
          <span className="output-label">Decision</span>
          <span className="output-text">{output.status}</span>
        </div>
        <div className="output-row">
          <span className="output-label">Reasoning</span>
          <span className="output-text">{output.reasoning}</span>
        </div>
        {weakPoints.length > 0 && (
          <details open className="output-details">
            <summary>Weak Points ({weakPoints.length})</summary>
            <div className="output-list">
              <ul>
                {weakPoints.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          </details>
        )}
        {output.retry_directive && (
          <div className="output-row">
            <span className="output-label">Retry Directive</span>
            <span className="output-text">{output.retry_directive}</span>
          </div>
        )}
        {output.status && (
          <div className={`critic-verdict ${String(output.status).toLowerCase()}`}>
            {output.status === "APPROVED" ? "✓ APPROVED" : "✗ REJECTED"}
          </div>
        )}
      </div>
    );
  }

  if (agent === "Speaker") {
    return (
      <div className="output-block">
        <div className="output-text">{output.argument || output}</div>
      </div>
    );
  }

  return <div className="output-text">{JSON.stringify(output, null, 2)}</div>;
}

function AgentCard({ team, agent, status, entry }) {
  const [isOpen, setIsOpen] = useState(true);
  useEffect(() => {
    if (entry) setIsOpen(true);
  }, [entry]);
  const hasContent = Boolean(entry);
  const displayStatus = hasContent && status === STATUS.IDLE ? STATUS.COMPLETE : status;
  const isActive = displayStatus === STATUS.ACTIVE;
  const isComplete = displayStatus === STATUS.COMPLETE || displayStatus === STATUS.APPROVED;
  const cardClass = `agent-card ${isActive ? "active" : ""} ${isComplete ? `done-${team.toLowerCase()}` : ""}`;
  const handleToggle = () => setIsOpen(prev => !prev);
  const output = entry?.content || null;

  return (
    <div className={cardClass}>
      <button type="button" className="agent-header" onClick={handleToggle}>
        <div className="agent-name-row">
          <div className="agent-icon">{AGENT_ICONS[agent] || agent[0]}</div>
          <div>
            <div className="agent-label">{agent}</div>
            <div className="agent-sublabel">
              {isActive ? "Thinking..." : (STATUS_LABEL[displayStatus] || "Waiting")}
            </div>
          </div>
        </div>
        <div className="agent-status">
          <StatusDot status={displayStatus} />
          <span className={`toggle-chevron ${isOpen ? "open" : ""}`}>▼</span>
        </div>
      </button>
      {isOpen && (
        <div className="agent-body open">
          <AgentOutput agent={agent} output={output} />
        </div>
      )}
    </div>
  );
}

function TeamColumn({ team, name, stance, agentStates, latestByAgent, round }) {
  const teamClass = team === "A" ? "team-a" : "team-b";
  const teamLabel = name || (team === "A" ? "Team A" : "Team B");
  const positionLabel = stance || name;

  return (
    <div className={`team-col ${teamClass}`}>
      <div className="team-header">
        <div className="team-badge">{teamLabel}</div>
      </div>
      <div className="team-position">
        {positionLabel ? `Arguing for: ${positionLabel}` : "Awaiting stance."}
      </div>

      {AGENTS.map((agent, index) => (
        <Fragment key={`${team}-${agent}`}>
          <AgentCard
            team={team}
            agent={agent}
            status={agentStates[agent]}
            entry={latestByAgent?.[round]?.[agent]}
          />
          {index < AGENTS.length - 1 && <div className="flow-arrow">↓</div>}
        </Fragment>
      ))}

    </div>
  );
}

function RoundView({ roundIndex, activeRound, children }) {
  if (roundIndex !== activeRound) return null;
  return (
    <div className="round-view">
      {children}
    </div>
  );
}

function JudgesPanel({ truthReport, verdict, teams }) {
  const claims = toArray(truthReport?.claims);
  const penalties = toArray(verdict?.penalties);
  const winnerTeam = verdict?.winner === "Team A" ? "A" : verdict?.winner === "Team B" ? "B" : null;
  const winnerColorClass = winnerTeam ? `team-${winnerTeam.toLowerCase()}` : "";
  const winnerLabel = winnerTeam && teams[winnerTeam] ? teams[winnerTeam] : verdict?.winner || "";
  const scoreA = verdict?.team_a_scores?.overall ?? "-";
  const scoreB = verdict?.team_b_scores?.overall ?? "-";
  const penaltyMatch = penalties.join(" ").match(/-?\d+(?:\.\d+)?/);
  const penaltyIcon = penalties.length > 0
    ? (penaltyMatch
      ? (penaltyMatch[0].startsWith("-") ? penaltyMatch[0] : `-${penaltyMatch[0]}`)
      : "-")
    : "";

  return (
    <div className="judge-section">
      <div className="judge-header">
        <div className="judge-title">Judge Panel</div>
        <div className="judge-subtitle">Isolated · Transcript only · Gemini 2.5 Pro</div>
      </div>

      <div className="judge-grid">
        <div className="judge-card">
          <div className="judge-card-header">
            <div className="judge-icon">⚖</div>
            <div>
              <div className="judge-card-name">Clerk</div>
              <div className="judge-card-sub">Fact verifier · Tavily</div>
            </div>
          </div>
          <div className="judge-card-body">
            <div className="section-label">Truth Report</div>
            {claims.length === 0 && <div className="claim-empty">Awaiting transcript review.</div>}
            {claims.map((claim, i) => (
              <div key={i} className="claim-row">
                <div className={`claim-badge ${claim.verdict?.toLowerCase()}`}>{claim.verdict}</div>
                <div className="claim-text">{claim.team === "Team A" ? teams.A || "Team A" : teams.B || "Team B"}: {claim.claim}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="judge-card">
          <div className="judge-card-header">
            <div className="judge-icon">🧠</div>
            <div>
              <div className="judge-card-name">Analyst</div>
              <div className="judge-card-sub">Logic scorer · Truth Report input</div>
            </div>
          </div>
          <div className="judge-card-body">
            <div className="section-label">Logic Scores</div>
            <div className="metric-bars">
              <div className="metric-row">
                <div className="metric-val a">{verdict?.team_a_scores?.factual_accuracy ?? "-"}</div>
                <div className="bar-track">
                  <div className="bar-a" style={{ flex: verdict?.team_a_scores?.factual_accuracy ?? 0 }} />
                  <div className="bar-b" style={{ flex: verdict?.team_b_scores?.factual_accuracy ?? 0 }} />
                </div>
                <div className="metric-val b">{verdict?.team_b_scores?.factual_accuracy ?? "-"}</div>
                <div className="metric-name">Factual accuracy</div>
              </div>
              <div className="metric-row">
                <div className="metric-val a">{verdict?.team_a_scores?.logical_consistency ?? "-"}</div>
                <div className="bar-track">
                  <div className="bar-a" style={{ flex: verdict?.team_a_scores?.logical_consistency ?? 0 }} />
                  <div className="bar-b" style={{ flex: verdict?.team_b_scores?.logical_consistency ?? 0 }} />
                </div>
                <div className="metric-val b">{verdict?.team_b_scores?.logical_consistency ?? "-"}</div>
                <div className="metric-name">Logical consistency</div>
              </div>
              <div className="metric-row">
                <div className="metric-val a">{verdict?.team_a_scores?.rebuttal_effectiveness ?? "-"}</div>
                <div className="bar-track">
                  <div className="bar-a" style={{ flex: verdict?.team_a_scores?.rebuttal_effectiveness ?? 0 }} />
                  <div className="bar-b" style={{ flex: verdict?.team_b_scores?.rebuttal_effectiveness ?? 0 }} />
                </div>
                <div className="metric-val b">{verdict?.team_b_scores?.rebuttal_effectiveness ?? "-"}</div>
                <div className="metric-name">Rebuttal effectiveness</div>
              </div>
              <div className="metric-row">
                <div className="metric-val a" style={{ fontSize: "12px", fontWeight: 500 }}>{scoreA}</div>
                <div className="bar-track">
                  <div className="bar-a" style={{ flex: typeof scoreA === "number" ? scoreA * 10 : 0 }} />
                  <div className="bar-b" style={{ flex: typeof scoreB === "number" ? scoreB * 10 : 0 }} />
                </div>
                <div className="metric-val b" style={{ fontSize: "12px", fontWeight: 500 }}>{scoreB}</div>
                <div className="metric-name" style={{ color: "var(--text-dim)" }}>Overall</div>
              </div>
            </div>
            <div className="claim-summary">
              <div className="section-label">Claim Breakdown</div>
              <div className="claim-summary-stats">
                <div className="claim-stat verified">
                  <span className="claim-stat-count">{claims.filter(c => c.verdict === "verified").length}</span>
                  <span className="claim-stat-label">Verified</span>
                </div>
                <div className="claim-stat false">
                  <span className="claim-stat-count">{claims.filter(c => c.verdict === "false").length}</span>
                  <span className="claim-stat-label">False</span>
                </div>
                <div className="claim-stat unverified">
                  <span className="claim-stat-count">{claims.filter(c => c.verdict === "unverified").length}</span>
                  <span className="claim-stat-label">Unverified</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className={`verdict-banner ${winnerColorClass}`}>
        <div className="verdict-top">
          <div className="verdict-winner-block">
            <div className="verdict-eyebrow">Final Verdict</div>
            <div className="verdict-winner">
              {verdict?.winner
                ? `${winnerLabel || verdict.winner} wins`
                : "Pending verdict"}
            </div>
            <div className="verdict-margin">{verdict?.summary || "Decisive - factual accuracy and rebuttal quality"}</div>
          </div>
          <div className="score-block">
            <div className="score-side">
              <div className="score-num a">{scoreA}</div>
              <div className="score-label">{teams.A || "Team A"}</div>
            </div>
            <div className="score-vs">vs</div>
            <div className="score-side">
              <div className="score-num b">{scoreB}</div>
              <div className="score-label">{teams.B || "Team B"}</div>
            </div>
          </div>
        </div>

        <div className="verdict-statement">
          <div className="statement-label">Analyst's Written Statement</div>
          <div className="statement-body">
            {verdict?.written_analysis ? (
              verdict.written_analysis.split("\n").filter(Boolean).map((line, i) => (
                <p key={i}>{line}</p>
              ))
            ) : (
              <p>Awaiting final statement.</p>
            )}
          </div>
          {penalties.length > 0 && (
            <div className="penalty-row">
              <div className="penalty-icon">{penaltyIcon}</div>
              <div className="penalty-text">{penalties.join(" - ")}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const {
    phase,
    query,
    setQuery,
    topic,
    teams,
    stances,
    judicialFocus,
    round,
    agentStates,
    agentHistory,
    verdict,
    truthReport,
    status,
    error,
    clarificationMessage,
    originalQuery,
    roundBanner,
    startDebate
  } = useDebate();

  const [activeRound, setActiveRound] = useState(1);

  useEffect(() => {
    if (phase === "verdict") {
      setActiveRound(3);
      return;
    }
    if (phase === "debate") {
      if (round >= 2) {
        setActiveRound(Math.min(round, 2));
        return;
      }
      setActiveRound(1);
    }
  }, [phase, round]);

  const latestByAgent = useMemo(() => {
    const latest = { A: {}, B: {} };
    agentHistory.A.forEach(item => {
      const r = item.round;
      latest.A[r] = latest.A[r] || {};
      latest.A[r][item.agent] = item;
    });
    agentHistory.B.forEach(item => {
      const r = item.round;
      latest.B[r] = latest.B[r] || {};
      latest.B[r][item.agent] = item;
    });
    return latest;
  }, [agentHistory]);

  const hasVerdict = Boolean(verdict);
  const headerTopic = topic || "Awaiting topic";

  const roundTabs = [
    { id: 1, label: "Round I" },
    { id: 2, label: "Round II" },
    { id: 3, label: "Verdict" },
  ];

  return (
    <div className="arena-root">
      {error && <div className="error-banner">ERROR: {error}</div>}

      {phase === "input" && (
        <div className="input-screen">
          <div className="input-card">
            <div className="header-title">STOA</div>
            <p className="input-sub">Two AI teams. Two rounds. One winner. Real-time debate.</p>
            <label className="input-label" htmlFor="query">Debate Question</label>
            <input
              id="query"
              className="input-field"
              placeholder="Enter a debate topic — e.g. Capitalism vs Socialism"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && startDebate()}
            />
            <button className="debate-btn" onClick={startDebate}>Initiate Debate</button>
            <div className="seed-section">
              <div className="seed-label">or pick a debate</div>
              <div className="seed-grid">
                {SEED_QUESTIONS.map(q => (
                  <button
                    key={q}
                    type="button"
                    className="seed-pill"
                    onClick={() => { setQuery(q); setTimeout(startDebate, 0); }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {phase === "clarification" && (
        <div className="input-screen">
          <div className="input-card">
            <div className="header-eyebrow">Multi-Agent Adversarial Framework</div>
            <div className="header-title">STOA</div>
            <div className="clarification-notice">
              <div className="clarification-notice-icon">!</div>
              <p className="clarification-notice-text">{clarificationMessage}</p>
            </div>
            {originalQuery && (
              <div className="original-query-banner">
                Your query: <span>"{originalQuery}"</span>
              </div>
            )}
            <label className="input-label" htmlFor="clarify-query">Revise your debate question</label>
            <input
              id="clarify-query"
              className="input-field"
              placeholder="Enter a clearer debate topic - e.g. Python vs JavaScript"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && startDebate()}
            />
            <button className="debate-btn" onClick={startDebate}>Retry Debate</button>
          </div>
        </div>
      )}

      {phase === "submitting" && (
        <div className="input-screen">
          <div className="input-card">
            <div className="header-eyebrow">Multi-Agent Adversarial Framework</div>
            <div className="header-title">STOA</div>
            <p className="input-sub">Analyzing your query...</p>
            <div className="query-preview">
              <span className="query-preview-label">Query:</span>
              <span className="query-preview-text">"{query}"</span>
            </div>
            <div className="spinner" />
          </div>
        </div>
      )}

      {(phase === "debate" || phase === "verdict") && (
        <>
          <div className="header">
            <div className="header-eyebrow">Multi-Agent Adversarial Framework</div>
            <div className="header-title">STOA</div>
            <div className="topic-pill">Topic: <span>{headerTopic}</span></div>
          </div>

          <div className="round-tabs">
            {roundTabs.map(tab => (
              <button
                key={tab.id}
                type="button"
                className={`round-tab ${activeRound === tab.id ? "active" : ""}`}
                onClick={() => setActiveRound(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="status-bar">
            <div className="status-dot running" />
            {status || "Arena idle"}
            {toArray(judicialFocus).length > 0 && (
              <div className="status-focus">
                <span>Judicial Focus</span>
                {toArray(judicialFocus).map((item, i) => (
                  <span key={i} className="focus-pill">{item}</span>
                ))}
              </div>
            )}
            {hasVerdict && <span className="status-complete">COMPLETE</span>}
          </div>

          {roundBanner && (
            <div className="round-banner" key={roundBanner.from}>
              <span className="round-banner-icon">⟳</span>
              Round {roundBanner.from} complete &middot; Round {roundBanner.to} beginning
            </div>
          )}

          <RoundView roundIndex={1} activeRound={activeRound}>
            <div className="arena-floor">
              <TeamColumn
                team="A"
                name={teams.A}
                stance={stances.A}
                agentStates={agentStates.A}
                latestByAgent={latestByAgent.A}
                round={1}
              />
              <div className="connector-col">
                <div className="vs-divider">VS</div>
                <div className="flow-line"></div>
              </div>
              <TeamColumn
                team="B"
                name={teams.B}
                stance={stances.B}
                agentStates={agentStates.B}
                latestByAgent={latestByAgent.B}
                round={1}
              />
            </div>
          </RoundView>

          <RoundView roundIndex={2} activeRound={activeRound}>
            <div className="arena-floor">
              <TeamColumn
                team="A"
                name={teams.A}
                stance={stances.A}
                agentStates={agentStates.A}
                latestByAgent={latestByAgent.A}
                round={2}
              />
              <div className="connector-col">
                <div className="vs-divider">VS</div>
                <div className="flow-line"></div>
              </div>
              <TeamColumn
                team="B"
                name={teams.B}
                stance={stances.B}
                agentStates={agentStates.B}
                latestByAgent={latestByAgent.B}
                round={2}
              />
            </div>
          </RoundView>

          <RoundView roundIndex={3} activeRound={activeRound}>
            <JudgesPanel truthReport={truthReport} verdict={verdict} teams={teams} />
          </RoundView>
        </>
      )}
    </div>
  );
}
