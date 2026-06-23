from typing import Annotated, Optional
from typing_extensions import TypedDict


def merge_teams(existing: dict[str, dict], new_data: dict[str, dict]) -> dict[str, dict]:
    updated = existing.copy() if existing else {}
    for team_id, data in new_data.items():
        if team_id not in updated:
            updated[team_id] = {}
        updated[team_id] = {**updated[team_id], **data}
    return updated

class TeamState(TypedDict, total=False):
    strategy: Optional[str]
    evidence: Optional[str]
    critic_status: Optional[str]
    critic_decision: Optional[str]
    retry_count: int
    weakness_flag: bool
    argument: Optional[str]


class STOAState(TypedDict):
    user_query: str
    arena_manifest: Optional[dict]
    clarification_needed: Optional[bool]
    clarification_response: Optional[str]

    current_round: int
    max_rounds: int

    teams: Annotated[dict[str, TeamState], merge_teams]

    debate_history: list[dict]

    truth_report: Optional[str]
    final_verdict: Optional[str]
    winner: Optional[str]