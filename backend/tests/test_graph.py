import json
from backend.models.state import STOAState
from backend.core.graph import stoa_graph


def main():
    print("=" * 60)
    print("STOA END-TO-END TEST")
    print("=" * 60 + "\n")

    initial_state: STOAState = {
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
        "team_a_retry_count": 0,
        "team_a_weakness_flag": False,
        "team_a_argument": None,
        "team_b_strategy": None,
        "team_b_evidence": None,
        "team_b_critic_status": None,
        "team_b_critic_decision": None,
        "team_b_retry_count": 0,
        "team_b_weakness_flag": False,
        "team_b_argument": None,
        "truth_report": None,
        "final_verdict": None,
        "winner": None
    }

    try:
        print("Invoking STOA graph...\n")
        final_state = stoa_graph.invoke(initial_state)

        #  Debate History
        print("\n" + "=" * 60)
        print("DEBATE TRANSCRIPT")
        print("=" * 60)
        for round_entry in final_state.get("debate_history", []):
            print(f"\n--- ROUND {round_entry['round']} ---")
            print(f"\n[TEAM A]\n{round_entry.get('team_a', '')}")
            print(f"\n[TEAM B]\n{round_entry.get('team_b', '')}")

        # --- Truth Report ---
        print("\n" + "=" * 60)
        print("🔍 TRUTH REPORT")
        print("=" * 60)
        truth_report_json = final_state.get("truth_report")
        if truth_report_json:
            print(json.dumps(json.loads(truth_report_json), indent=2))
        else:
            print("No truth report generated.")

        #  Final Verdict
        print("\n" + "=" * 60)
        print(" FINAL VERDICT")
        print("=" * 60)
        final_verdict_json = final_state.get("final_verdict")
        if final_verdict_json:
            print(json.dumps(json.loads(final_verdict_json), indent=2))
        else:
            print("No final verdict generated.")

        # Winner Banner
        winner = final_state.get("winner")
        if winner:
            print(f"\n🏆 WINNER: {winner}")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()