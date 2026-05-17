from langchain_core.prompts import ChatPromptTemplate

from backend.models.schemas import TruthReport
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt
from backend.llm.gemini import judge_llm
from backend.tools.search import perform_research

_prompt = load_prompt("judges.yaml", "clerk")

structured_llm = judge_llm.with_structured_output(TruthReport)

CLERK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

clerk_chain = CLERK_PROMPT | structured_llm


def _extract_claims_for_search(debate_history: list[dict]) -> list[str]:
    """Build search queries from debate arguments to verify claims."""
    queries = []
    for round_entry in debate_history:
        team_a_arg = round_entry.get("team_a", "")
        team_b_arg = round_entry.get("team_b", "")
        # Extract one search query per round per team — keep it focused
        if team_a_arg:
            queries.append(f"fact check: {team_a_arg[:100]}")
        if team_b_arg:
            queries.append(f"fact check: {team_b_arg[:100]}")
    return queries


def _format_transcript(debate_history: list[dict]) -> str:
    """Format debate history into a clean readable transcript."""
    transcript = ""
    for round_entry in debate_history:
        transcript += f"\n--- ROUND {round_entry['round']} ---\n"
        transcript += f"\nTEAM A:\n{round_entry.get('team_a', '')}\n"
        transcript += f"\nTEAM B:\n{round_entry.get('team_b', '')}\n"
    return transcript


def clerk_node(state: STOAState) -> dict:
    """Clerk agent — extracts and verifies all factual claims from the debate."""
    debate_history = state["debate_history"]

    print("\n[Clerk] Extracting claims and running verification searches...")

    # 1. Build search queries from the debate arguments
    queries = _extract_claims_for_search(debate_history)
    search_results = perform_research(queries)

    # 2. Format the full transcript
    transcript = _format_transcript(debate_history)

    # 3. Run the Clerk LLM
    output: TruthReport = clerk_chain.invoke({
        "debate_transcript": transcript,
        "search_results": search_results
    })

    print(f"[Clerk] Truth Report complete — {output.verified_count} verified, {output.false_count} false, {output.unverified_count} unverified.")

    return {"truth_report": output.model_dump_json()}