import json
from backend.core.graph import stoa_graph


def main():
    print("=" * 50)
    print("STOA END-TO-END TEST: BOTH TEAMS")
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

        print(f"\nTeam A critic status : {final_state.get('team_a_critic_status')}")
        print(f"Team A retry count   : {final_state.get('team_a_retry_count')}")
        print(f"Team A weakness flag : {final_state.get('team_a_weakness_flag')}")

        print(f"\nTeam B critic status : {final_state.get('team_b_critic_status')}")
        print(f"Team B retry count   : {final_state.get('team_b_retry_count')}")
        print(f"Team B weakness flag : {final_state.get('team_b_weakness_flag')}")

        argument_a = final_state.get("team_a_argument")
        argument_b = final_state.get("team_b_argument")

        if argument_a:
            print("\n" + "=" * 50)
            print("TEAM A ARGUMENT")
            print("=" * 50)
            print(argument_a)
        else:
            print("\nNo Team A argument produced.")

        if argument_b:
            print("\n" + "=" * 50)
            print("TEAM B ARGUMENT")
            print("=" * 50)
            print(argument_b)
        else:
            print("\nNo Team B argument produced.")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()