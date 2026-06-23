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

    team_state = state.get("teams", {}).get(team_id, {})
    strategy_json = team_state.get("strategy")
    strategy_update = None
    if not strategy_json:
        strategy = StrategyDocument(
            win_condition="Missing strategy document.",
            core_claims=[],
            anticipated_attacks=[],
            research_directives=[]
        )
        strategy_json = strategy.model_dump_json()
        strategy_update = strategy_json
        print(f"\n[Researcher {team_id}] Missing strategy document. Using fallback.")
    else:
        try:
            strategy = StrategyDocument.model_validate_json(strategy_json)
        except Exception as exc:
            strategy = StrategyDocument(
                win_condition="Invalid strategy document.",
                core_claims=[],
                anticipated_attacks=[],
                research_directives=[]
            )
            strategy_json = strategy.model_dump_json()
            strategy_update = strategy_json
            print(f"\n[Researcher {team_id}] Invalid strategy document ({exc}). Using fallback.")

    critic_decision_json = team_state.get("critic_decision")

    queries = strategy.research_directives
    if critic_decision_json:
        try:
            critic_decision = CriticDecision.model_validate_json(critic_decision_json)
        except Exception as exc:
            critic_decision = None
            print(f"\n[Researcher {team_id}] Invalid critic decision ({exc}). Using original directives.")
        if critic_decision:
            retry_directive = critic_decision.retry_directive
            if isinstance(retry_directive, str) and retry_directive.strip():
                queries = [retry_directive]
                print(f"\n[Researcher {team_id}] RETRY — using Critic directive: {retry_directive}")
            else:
                print(f"\n[Researcher {team_id}] RETRY directive missing. Using original directives.")
    else:
        print(f"\n[Researcher {team_id}] Executing Tavily searches...")

    if not queries:
        search_context = "No research directives provided."
    else:
        search_context = perform_research(queries)

    output: EvidenceDocument = researcher_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "stance": team_data["stance"],
        "search_context": search_context,
        "research_directives": json.dumps(queries, indent=2)
    })

    team_update = {"evidence": output.model_dump_json()}
    if strategy_update:
        team_update["strategy"] = strategy_update
    return {"teams": {team_id: team_update}}


def make_researcher(team_id: str):
    def researcher_node(state: STOAState) -> dict:
        return run_researcher(state, team_id)
    return researcher_node
