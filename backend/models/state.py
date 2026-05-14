from typing import Optional
from typing_extensions import TypedDict


class STOAState(TypedDict):
    # Arena Setup
    user_query: str
    arena_manifest: Optional[dict]
    clarification_needed: Optional[bool]
    clarification_response: Optional[str]

    # Round Tracking
    current_round: int
    max_rounds: int

    # Team A Internal (isolated from Judge)
    team_a_strategy: Optional[str]
    team_a_evidence: Optional[str]
    team_a_critic_status: Optional[str]   # "APPROVED" / "REJECTED"
    team_a_retry_count: int
    team_a_weakness_flag: bool
    team_a_argument: Optional[str]

    # Team B Internal (isolated from Judge)
    team_b_strategy: Optional[str]
    team_b_evidence: Optional[str]
    team_b_critic_status: Optional[str]
    team_b_retry_count: int
    team_b_weakness_flag: bool
    team_b_argument: Optional[str]

    # Debate History
    debate_history: list[dict]

    # Judge Panel
    truth_report: Optional[str]
    final_verdict: Optional[str]
    winner: Optional[str]