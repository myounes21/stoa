from langchain_core.prompts import ChatPromptTemplate

from backend.models.schemas import FinalVerdict
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt
from backend.llm.gemini import judge_llm

_prompt = load_prompt("judges.yaml", "analyst")

structured_llm = judge_llm.with_structured_output(FinalVerdict)

ANALYST_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

analyst_chain = ANALYST_PROMPT | structured_llm

def _format_transcript(debate_history: list[dict], team_a_name: str, team_b_name: str) -> str:
    transcript = ""
    for round_entry in debate_history:
        transcript += f"\n--- ROUND {round_entry['round']} ---\n"
        transcript += f"\n{team_a_name}:\n{round_entry.get('team_a', '')}\n"
        transcript += f"\n{team_b_name}:\n{round_entry.get('team_b', '')}\n"
    return transcript

def analyst_node(state: STOAState) -> dict:
    """Analyst agent — scores both teams and declares the winner."""
    debate_history = state["debate_history"]
    truth_report = state["truth_report"]

    print("\n[Analyst] Evaluating arguments and producing final verdict...")

    manifest = state.get("arena_manifest") or {}
    team_a_name = (manifest.get("team_a") or {}).get("team_name") or "Team A"
    team_b_name = (manifest.get("team_b") or {}).get("team_name") or "Team B"

    transcript = _format_transcript(debate_history, team_a_name, team_b_name)

    output: FinalVerdict = analyst_chain.invoke({
        "team_a_name": team_a_name,
        "team_b_name": team_b_name,
        "debate_transcript": transcript,
        "truth_report": truth_report
    })

    print(f"[Analyst] Verdict: {output.winner} wins.")

    return {
        "final_verdict": output.model_dump_json(),
        "winner": output.winner
    }
