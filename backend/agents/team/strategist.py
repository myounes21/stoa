from langchain_core.prompts import ChatPromptTemplate
import json

from backend.models.schemas import StrategyDocument
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt
from backend.llm.groq import team_llm

_prompt = load_prompt("teams.yaml", "strategist")

structured_llm = team_llm.with_structured_output(StrategyDocument)

STRATEGIST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

strategist_chain = STRATEGIST_PROMPT | structured_llm


def run_strategist(state: STOAState, team_id: str) -> dict:
    manifest = state["arena_manifest"]
    current_round = state["current_round"]
    team_data = manifest["team_a"] if team_id == "A" else manifest["team_b"]

    history_str = "No history yet (Round 1)."
    round_2_directive = ""

    if state.get("debate_history") and current_round > 1:
        history_str = json.dumps(state["debate_history"], indent=2)
        opponent_key = "team_b" if team_id == "A" else "team_a"
        last_opponent_argument = state["debate_history"][-1][opponent_key]

        round_2_directive = (
            f"ROUND 2 DIRECTIVE - THIS OVERRIDES EVERYTHING ELSE:\n"
            f"You are NOT rebuilding Round 1. You are executing a targeted demolition.\n\n"
            f"OPPONENT'S EXACT ARGUMENT YOU MUST DESTROY:\n"
            f"\"{last_opponent_argument}\"\n\n"
            f"Your core_claims must directly counter the specific points above.\n"
            f"Your research_directives must find evidence that refutes their exact claims.\n"
            f"Your win_condition must reference defeating their specific argument, not a generic stance."
        )

    output: StrategyDocument = strategist_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "stance": team_data["stance"],
        "judicial_focus": ", ".join(manifest["judicial_focus"]),
        "current_round": current_round,
        "debate_history": history_str,
        "round_2_directive": round_2_directive
    })

    if output is None:
        raise ValueError(f"Strategist (Team {team_id}) returned None.")

    if team_id == "A":
        return {"team_a_strategy": output.model_dump_json()}
    else:
        return {"team_b_strategy": output.model_dump_json()}


# LangGraph Node Wrappers
def strategist_node_a(state: STOAState) -> dict:
    return run_strategist(state, "A")


def strategist_node_b(state: STOAState) -> dict:
    return run_strategist(state, "B")