import json
from unittest.mock import patch
from backend.models.schemas import CriticDecision
from backend.core.graph import stoa_graph


def main():
    print("=" * 50)
    print("STOA RETRY LOOP TEST: TEAM A")
    print("=" * 50)

    mock_rejection = CriticDecision(
        status="REJECTED",
        reasoning="Evidence is weak and does not support core claims.",
        weak_points=["No concrete data", "Sources are unreliable"],
        retry_directive="One Piece named character count official source"
    )

    initial_state = {
        "user_query": "which is better one piece or attack on titan",
        "arena_manifest": None,
        "clarification_needed": None,
        "clarification_response": None,
        "current_round": 1,
        "max_rounds": 2,
        "debate_history": [],
        "team_a_strategy": None,
        "team_a_evidence": None,
        "team_a_critic_status": None,
        "team_a_critic_decision": None,
        "team_b_critic_decision": None,
        "team_a_retry_count": 0,
        "team_a_weakness_flag": False,
        "team_a_argument": None,
        "team_b_strategy": None,
        "team_b_evidence": None,
        "team_b_critic_status": None,
        "team_b_retry_count": 0,
        "team_b_weakness_flag": False,
        "team_b_argument": None,
        "truth_report": None,
        "final_verdict": None,
        "winner": None,
    }

    with patch("backend.agents.team.critic.critic_chain") as mock_chain:
        mock_chain.invoke.return_value = mock_rejection
        final_state = stoa_graph.invoke(initial_state)

    print("\n" + "=" * 50)
    print("RETRY LOOP RESULT")
    print("=" * 50)
    print(f"\nCritic status  : {final_state.get('team_a_critic_status')}")
    print(f"Retry count    : {final_state.get('team_a_retry_count')}")
    print(f"Weakness flag  : {final_state.get('team_a_weakness_flag')}")

    argument = final_state.get("team_a_argument")
    if argument:
        print("\n[TEAM A ARGUMENT - FORCED THROUGH]\n")
        print(argument)
    else:
        print("\nNo argument produced.")


if __name__ == "__main__":
    main()