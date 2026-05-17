from langchain_core.prompts import ChatPromptTemplate

from backend.models.schemas import CriticDecision
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt
from backend.llm.groq import team_llm

_prompt = load_prompt("teams.yaml", "critic")

structured_llm = team_llm.with_structured_output(CriticDecision)

CRITIC_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

critic_chain = CRITIC_PROMPT | structured_llm


def run_critic(state: STOAState, team_id: str) -> dict:
    """Core critic logic, usable by both teams."""
    manifest = state["arena_manifest"]
    team_data = manifest["team_a"] if team_id == "A" else manifest["team_b"]

    retry_count = state["team_a_retry_count"] if team_id == "A" else state["team_b_retry_count"]
    strategy_json = state["team_a_strategy"] if team_id == "A" else state["team_b_strategy"]
    evidence_json = state["team_a_evidence"] if team_id == "A" else state["team_b_evidence"]

    # Force approve if max retries reached — no LLM call needed
    if retry_count >= 2:
        print(f"\n[Critic {team_id}] Max retries reached. Force approving with weakness flag.")
        force_decision = CriticDecision(
            status="APPROVED",
            reasoning="Force approved after maximum retries. Evidence quality could not be improved.",
            weak_points=["Evidence failed Critic audit twice — treat all claims with caution"],
            retry_directive=None
        )
        if team_id == "A":
            return {
                "team_a_critic_status": "APPROVED",
                "team_a_critic_decision": force_decision.model_dump_json(),
                "team_a_weakness_flag": True
            }
        else:
            return {
                "team_b_critic_status": "APPROVED",
                "team_b_critic_decision": force_decision.model_dump_json(),
                "team_b_weakness_flag": True
            }

    # Run the LLM audit
    output: CriticDecision = critic_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "strategy": strategy_json,
        "evidence": evidence_json
    })

    print(f"\n[Critic {team_id}] Verdict: {output.status}")
    print(f"[Critic {team_id}] Reasoning: {output.reasoning}")

    if team_id == "A":
        return {
            "team_a_critic_status": output.status,
            "team_a_critic_decision": output.model_dump_json(),
            "team_a_retry_count": retry_count + 1 if output.status == "REJECTED" else retry_count
        }
    else:
        return {
            "team_b_critic_status": output.status,
            "team_b_critic_decision": output.model_dump_json(),
            "team_b_retry_count": retry_count + 1 if output.status == "REJECTED" else retry_count
        }


# LangGraph Node Wrappers
def critic_node_a(state: STOAState) -> dict:
    return run_critic(state, "A")


def critic_node_b(state: STOAState) -> dict:
    return run_critic(state, "B")


# Conditional Edge Routers
def critic_router_a(state: STOAState) -> str:
    if state["team_a_critic_status"] == "APPROVED":
        return "speaker_a"
    return "researcher_a"


def critic_router_b(state: STOAState) -> str:
    if state["team_b_critic_status"] == "APPROVED":
        return "speaker_b"
    return "researcher_b"