from langchain_core.prompts import ChatPromptTemplate

from backend.models.schemas import CriticDecision, SpeakerOutput
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt
from backend.llm.groq import team_llm

_prompt = load_prompt("teams.yaml", "speaker")

structured_llm = team_llm.with_structured_output(SpeakerOutput)

SPEAKER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

speaker_chain = SPEAKER_PROMPT | structured_llm


def get_opponent_argument(state: STOAState, team_id: str) -> str:
    """Extract the opponent's last argument from debate history."""
    if state["current_round"] == 1:
        return "No opponent argument yet. This is Round 1."

    history = state.get("debate_history", [])
    if not history:
        return "No opponent argument available."

    last_round = history[-1]

    opponent_id = "B" if team_id == "A" else "A"
    return last_round.get(f"team_{opponent_id.lower()}", "No opponent argument available.")


def run_speaker(state: STOAState, team_id: str) -> dict:
    """core speaker logic."""
    manifest = state["arena_manifest"]
    team_data = manifest["team_a"] if team_id == "A" else manifest["team_b"]

    team_state = state.get("teams", {}).get(team_id, {})
    strategy_json = team_state.get("strategy")
    evidence_json = team_state.get("evidence")
    opponent_argument = get_opponent_argument(state, team_id)

    critic_decision_json = team_state.get("critic_decision")
    weak_points = []
    if critic_decision_json:
        critic_decision = CriticDecision.model_validate_json(critic_decision_json)
        weak_points = critic_decision.weak_points

    weak_points_str = "\n".join(f"- {p}" for p in weak_points) if weak_points else "None identified."

    print(f"\n[Speaker {team_id}] Delivering argument for Round {state['current_round']}...")

    output: SpeakerOutput = speaker_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "stance": team_data["stance"],
        "current_round": state["current_round"],
        "strategy": strategy_json,
        "evidence": evidence_json,
        "opponent_argument": opponent_argument,
        "weak_points": weak_points_str
    })

    print(f"[Speaker {team_id}] Argument delivered.")

    return {"teams": {team_id: {"argument": output.argument}}}


def make_speaker(team_id: str):
    def speaker_node(state: STOAState) -> dict:
        return run_speaker(state, team_id)
    return speaker_node