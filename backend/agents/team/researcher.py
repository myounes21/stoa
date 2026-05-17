import json
from langchain_core.prompts import ChatPromptTemplate

from backend.models.schemas import CriticDecision, EvidenceDocument, StrategyDocument
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

    # 1. Get the strategy document
    strategy_json = state["team_a_strategy"] if team_id == "A" else state["team_b_strategy"]
    strategy = StrategyDocument.model_validate_json(strategy_json)

    # 2. Determine search queries — use retry_directive if this is a retry
    critic_decision_json = state.get("team_a_critic_decision") if team_id == "A" else state.get("team_b_critic_decision")

    if critic_decision_json:
        critic_decision = CriticDecision.model_validate_json(critic_decision_json)
        queries = [critic_decision.retry_directive]
        print(f"\n[Researcher {team_id}] RETRY — using Critic directive: {critic_decision.retry_directive}")
    else:
        queries = strategy.research_directives
        print(f"\n[Researcher {team_id}] Executing Tavily searches...")

    search_context = perform_research(queries)

    # 3. Synthesize evidence
    output: EvidenceDocument = researcher_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "stance": team_data["stance"],
        "search_context": search_context,
        "research_directives": json.dumps(queries, indent=2)
    })

    if team_id == "A":
        return {"team_a_evidence": output.model_dump_json()}
    else:
        return {"team_b_evidence": output.model_dump_json()}


# LangGraph Node Wrappers
def researcher_node_a(state: STOAState) -> dict:
    return run_researcher(state, "A")


def researcher_node_b(state: STOAState) -> dict:
    return run_researcher(state, "B")