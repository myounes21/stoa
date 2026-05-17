import json
from langchain_core.prompts import ChatPromptTemplate

from backend.models.schemas import EvidenceDocument, StrategyDocument
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt
from backend.llm.groq import team_llm
from backend.tools.search import perform_research

_prompt = load_prompt("teams.yaml", "researcher")

structured_llm = team_llm.with_structured_output(EvidenceDocument)

RESEARCHER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

researcher_chain = RESEARCHER_PROMPT | structured_llm


def run_researcher(state: STOAState, team_id: str) -> dict:
    """Core logic for the researcher, usable by both Team A and Team B."""
    manifest = state["arena_manifest"]
    team_data = manifest["team_a"] if team_id == "A" else manifest["team_b"]

    # 1. Get the strategy document generated in the previous step
    strategy_json = state["team_a_strategy"] if team_id == "A" else state["team_b_strategy"]
    strategy = StrategyDocument.model_validate_json(strategy_json)

    # 2. Execute actual web searches using the directives
    print(f"\n🔍 [Researcher {team_id}] Executing Tavily searches...")
    search_context = perform_research(strategy.research_directives)

    # 3. Pass the raw results to the LLM to synthesize
    output: EvidenceDocument = researcher_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "stance": team_data["stance"],
        "search_context": search_context,
        "research_directives": json.dumps(strategy.research_directives, indent=2)
    })

    # 4. Return the state update specific to the active team
    if team_id == "A":
        return {"team_a_evidence": output.model_dump_json()}
    else:
        return {"team_b_evidence": output.model_dump_json()}


# LangGraph Node Wrappers
def researcher_node_a(state: STOAState) -> dict:
    return run_researcher(state, "A")


def researcher_node_b(state: STOAState) -> dict:
    return run_researcher(state, "B")