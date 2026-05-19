from typing import Annotated, Optional
from typing_extensions import TypedDict


def take_last(a, b):
    return b


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
    team_a_critic_status: Annotated[Optional[str], take_last]
    team_a_critic_decision: Annotated[Optional[str], take_last]
    team_a_retry_count: Annotated[int, take_last]
    team_a_weakness_flag: Annotated[bool, take_last]
    team_a_argument: Optional[str]

    # Team B Internal
    team_b_strategy: Optional[str]
    team_b_evidence: Optional[str]
    team_b_critic_status: Annotated[Optional[str], take_last]
    team_b_critic_decision: Annotated[Optional[str], take_last]
    team_b_retry_count: Annotated[int, take_last]
    team_b_weakness_flag: Annotated[bool, take_last]
    team_b_argument: Optional[str]

    # Debate History
    debate_history: list[dict]

    # Judge Panel
    truth_report: Optional[str]
    final_verdict: Optional[str]
    winner: Optional[str]