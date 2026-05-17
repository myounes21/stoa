import json
from backend.core.graph import stoa_graph

def main():
    print("=" * 50)
    print("STOA END-TO-END TEST: TEAM A FULL FLOW")
    print("=" * 50)

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

    try:
        final_state = stoa_graph.invoke(initial_state)

        print("\n" + "=" * 50)
        print("FINAL STATE SUMMARY")
        print("=" * 50)

        print(f"\nClarification needed: {final_state.get('clarification_needed')}")
        print(f"Current round: {final_state.get('current_round')}")
        print(f"Retry count: {final_state.get('team_a_retry_count')}")
        print(f"Weakness flag: {final_state.get('team_a_weakness_flag')}")
        print(f"Critic status: {final_state.get('team_a_critic_status')}")

        argument = final_state.get("team_a_argument")
        if argument:
            print("\n[TEAM A ARGUMENT]\n")
            print(argument)
        else:
            print("\nNo argument produced.")

    except Exception as e:
        print(f"\nError: {e}")
        raise

if __name__ == "__main__":
    main()