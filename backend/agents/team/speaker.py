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

    if team_id == "A":
        return last_round.get("team_b", "No opponent argument available.")
    else:
        return last_round.get("team_a", "No opponent argument available.")


def run_speaker(state: STOAState, team_id: str) -> dict:
    """core speaker logic."""
    manifest = state["arena_manifest"]
    team_data = manifest["team_a"] if team_id == "A" else manifest["team_b"]

    strategy_json = state["team_a_strategy"] if team_id == "A" else state["team_b_strategy"]
    evidence_json = state["team_a_evidence"] if team_id == "A" else state["team_b_evidence"]
    opponent_argument = get_opponent_argument(state, team_id)

    # Extract weak_points from Critic decision
    critic_decision_json = state.get("team_a_critic_decision") if team_id == "A" else state.get("team_b_critic_decision")
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

    if team_id == "A":
        return {"team_a_argument": output.argument}
    else:
        return {"team_b_argument": output.argument}

# LangGraph Node Wrappers
def speaker_node_a(state: STOAState) -> dict:
    return run_speaker(state, "A")


def speaker_node_b(state: STOAState) -> dict:
    return run_speaker(state, "B")