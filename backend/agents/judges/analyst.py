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

def _format_transcript(debate_history: list[dict]) -> str:
    transcript = ""
    for round_entry in debate_history:
        transcript += f"\n--- ROUND {round_entry['round']} ---\n"
        transcript += f"\nTEAM A:\n{round_entry.get('team_a', '')}\n"
        transcript += f"\nTEAM B:\n{round_entry.get('team_b', '')}\n"
    return transcript

def analyst_node(state: STOAState) -> dict:
    """Analyst agent — scores both teams and declares the winner."""
    debate_history = state["debate_history"]
    truth_report = state["truth_report"]

    print("\n[Analyst] Evaluating arguments and producing final verdict...")

    transcript = _format_transcript(debate_history)

    output: FinalVerdict = analyst_chain.invoke({
        "debate_transcript": transcript,
        "truth_report": truth_report
    })

    print(f"[Analyst] Verdict: {output.winner} wins.")

    return {
        "final_verdict": output.model_dump_json(),
        "winner": output.winner
    }