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
    """Core logic for the strategist, usable by both Team A and Team B."""
    manifest = state["arena_manifest"]

    # Determine which team's data to pull from the manifest
    team_data = manifest["team_a"] if team_id == "A" else manifest["team_b"]

    # Format the debate history nicely for the LLM
    history_str = "No history yet (Round 1)."
    if state.get("debate_history"):
        history_str = json.dumps(state["debate_history"], indent=2)

    # Invoke the LLM
    output: StrategyDocument = strategist_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "stance": team_data["stance"],
        "judicial_focus": ", ".join(manifest["judicial_focus"]),
        "current_round": state["current_round"],
        "debate_history": history_str
    })

    # Return the state update specific to the active team
    if team_id == "A":
        return {"team_a_strategy": output.model_dump_json()}
    else:
        return {"team_b_strategy": output.model_dump_json()}


# LangGraph Node Wrappers
def strategist_node_a(state: STOAState) -> dict:
    return run_strategist(state, "A")


def strategist_node_b(state: STOAState) -> dict:
    return run_strategist(state, "B")