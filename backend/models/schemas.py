import uuid
from typing import List
from pydantic import BaseModel, Field
from backend.config import settings


class TeamMission(BaseModel):
    """
    Defines the identity and strategy for a specific side in the STOA Arena.
    """
    team_name: str = Field(description="The name of the contender (e.g., 'React', 'Team Monolith')")
    stance: str = Field(description="The core philosophy or technical position this team must defend.")
    mission_goal: str = Field(description="The specific 'Win Condition' — what the agent needs to prove to the Judge.")


class ArenaManifest(BaseModel):
    """
    The Single Source of Truth for a STOA adversarial session.
    This JSON governs exactly how the debate will unfold.
    """
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the session."
    )

    # The Conflict
    topic: str = Field(description="The high-level subject or user question.")

    # The Contenders
    team_a: TeamMission
    team_b: TeamMission

    # Governance
    judicial_focus: List[str] = Field(
        default=["logical consistency", "factual accuracy", "rebuttal quality"],
        description="The rubric the Judge will use to score the debate."
    )

    max_rounds: int = Field(default_factory=lambda: settings.MAX_ROUNDS)
