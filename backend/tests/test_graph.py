from backend.core.graph import stoa_graph


def main():
    print("=" * 50)
    print("STOA END-TO-END TEST: 2 ROUNDS")
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
        print("DEBATE HISTORY")
        print("=" * 50)

        for round_entry in final_state.get("debate_history", []):
            print(f"\n--- ROUND {round_entry['round']} ---")
            print(f"\nTEAM A:\n{round_entry['team_a']}")
            print(f"\nTEAM B:\n{round_entry['team_b']}")

        print(f"\nFinal round reached: {final_state.get('current_round') - 1}")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()