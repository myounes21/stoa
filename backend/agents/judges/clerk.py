import json
from langchain_core.prompts import ChatPromptTemplate

from backend.models.schemas import TruthReport, ClaimsList
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt
from backend.llm.gemini import judge_llm
from backend.tools.search import perform_research

_prompt = load_prompt("judges.yaml", "clerk")

structured_llm = judge_llm.with_structured_output(TruthReport)

EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["extract_system"]),
    ("human", _prompt["extract_human"])
])

VERIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

extract_chain = EXTRACT_PROMPT | judge_llm.with_structured_output(ClaimsList)
verify_chain = VERIFY_PROMPT | structured_llm


def _format_transcript(debate_history: list[dict]) -> str:
    transcript = ""
    for round_entry in debate_history:
        transcript += f"\n--- ROUND {round_entry['round']} ---\n"
        transcript += f"\nTEAM A:\n{round_entry.get('team_a', '')}\n"
        transcript += f"\nTEAM B:\n{round_entry.get('team_b', '')}\n"
    return transcript


def clerk_node(state: STOAState) -> dict:
    """Clerk agent — extracts and verifies all factual claims from the debate."""
    debate_history = state["debate_history"]
    transcript = _format_transcript(debate_history)

    print("\n[Clerk] Step 1: Extracting specific factual claims from transcript...")

    claims_output: ClaimsList = extract_chain.invoke({
        "debate_transcript": transcript
    })

    claims = claims_output.claims
    print(f"[Clerk] Extracted {len(claims)} claims. Running targeted searches...")

    search_results = perform_research(claims)

    print(f"[Clerk] Step 2: Verifying claims against search results...")

    output: TruthReport = verify_chain.invoke({
        "debate_transcript": transcript,
        "search_results": search_results
    })

    print(f"[Clerk] Truth Report complete — {output.verified_count} verified, "
          f"{output.false_count} false, {output.unverified_count} unverified.")

    return {"truth_report": output.model_dump_json()}