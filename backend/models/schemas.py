import uuid
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.config import settings

class TeamMission(BaseModel):
    team_name: str = Field(description="The name of the contender (e.g., 'Team Python')")
    stance: str = Field(description="A single declarative sentence the team will defend.")
    mission_goal: str = Field(description="What the team must prove to WIN — specific, not vague.")

class ArenaManifestLLM(BaseModel):
    """What the LLM is responsible for generating if the debate is valid."""
    topic: str = Field(description="The high-level subject or user question.")
    team_a: TeamMission
    team_b: TeamMission
    judicial_focus: List[str] = Field(
        description="The rubric the Judge will use to score the debate."
    )

class DispatcherOutput(BaseModel):
    """The master output for the Dispatcher LLM. It chooses to either clarify OR generate a manifest."""
    clarification_needed: bool = Field(
        description="Set to True ONLY if the user's query is too vague, open-ended, or lacks two clear sides (e.g., 'best anime'). Set to False if it's a clear comparison."
    )
    clarification_response: Optional[str] = Field(
        description="If clarification is needed, a brief response telling the user to provide two clear sides.",
        default=None
    )
    manifest: Optional[ArenaManifestLLM] = Field(
        description="If clarification is NOT needed, provide the fully generated debate manifest.",
        default=None
    )

class ArenaManifest(ArenaManifestLLM):
    """Full manifest with system-controlled fields added after LLM generation."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    max_rounds: int = Field(default_factory=lambda: settings.MAX_ROUNDS)