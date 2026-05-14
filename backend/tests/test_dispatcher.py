from backend.agents.dispatcher import dispatcher_node
from backend.models.state import STOAState

state: STOAState = {
    "user_query": "Is Python better than JavaScript for backend development?",
    "arena_manifest": None,
    "clarification_needed": None,
    "clarification_response": None,
    "current_round": 0,
    "max_rounds": 2,
    "team_a_strategy": None,
    "team_a_evidence": None,
    "team_a_critic_status": None,
    "team_a_retry_count": 0,
    "team_a_weakness_flag": False,
    "team_a_argument": None,
    "team_b_strategy": None,
    "team_b_evidence": None,
    "team_b_critic_status": None,
    "team_b_retry_count": 0,
    "team_b_weakness_flag": False,
    "team_b_argument": None,
    "debate_history": [],
    "truth_report": None,
    "final_verdict": None,
    "winner": None,
}

result = dispatcher_node(state)
print(result)