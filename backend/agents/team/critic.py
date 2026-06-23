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

    team_state = state.get("teams", {}).get(team_id, {})

    retry_count = team_state.get("retry_count", 0)
    strategy_json = team_state.get("strategy")
    evidence_json = team_state.get("evidence")

    if retry_count >= 2:
        print(f"\n[Critic {team_id}] Max retries reached. Force approving with weakness flag.")
        force_decision = CriticDecision(
            status="APPROVED",
            reasoning="Force approved after maximum retries. Evidence quality could not be improved.",
            weak_points=["Evidence failed Critic audit twice — treat all claims with caution"],
            retry_directive=None
        )
        return {
            "teams": {
                team_id: {
                    "critic_status": "APPROVED",
                    "critic_decision": force_decision.model_dump_json(),
                    "weakness_flag": True
                }
            }
        }

    output: CriticDecision = critic_chain.invoke({
        "team_name": team_data["team_name"],
        "topic": manifest["topic"],
        "strategy": strategy_json,
        "evidence": evidence_json
    })

    print(f"\n[Critic {team_id}] Verdict: {output.status}")
    print(f"[Critic {team_id}] Reasoning: {output.reasoning}")

    return {
        "teams": {
            team_id: {
                "critic_status": output.status,
                "critic_decision": output.model_dump_json(),
                "retry_count": retry_count + 1 if output.status == "REJECTED" else retry_count
            }
        }
    }


def make_critic(team_id: str):
    def critic_node(state: STOAState) -> dict:
        return run_critic(state, team_id)
    return critic_node


def make_critic_router(team_id: str):
    def critic_router(state: STOAState) -> str:
        status = state.get("teams", {}).get(team_id, {}).get("critic_status")
        if status == "APPROVED":
            return f"speaker_{team_id.lower()}"
        return f"researcher_{team_id.lower()}"
    return critic_router