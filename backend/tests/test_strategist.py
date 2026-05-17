import json
from backend.models.state import STOAState
from backend.agents.team.strategist import strategist_node_a


def main():
    print("==================================================")
    print("STOA STRATEGIST TEST: TEAM A (ONE PIECE)")
    print("==================================================\n")

    state: STOAState = {
        "user_query": "which is better one piece or attack on titan",
        "arena_manifest": {
            "topic": "One Piece vs Attack on Titan",
            "team_a": {
                "team_name": "Team One Piece",
                "stance": "One Piece is the better anime series.",
                "mission_goal": "Prove that One Piece's complex world-building, diverse cast of characters, and epic story arcs make it the superior choice for anime fans."
            },
            "team_b": {
                "team_name": "Team Attack on Titan",
                "stance": "Attack on Titan is the better anime series.",
                "mission_goal": "Prove that Attack on Titan's dark and suspenseful storytelling, deep character development, and intense action sequences make it the more compelling and engaging anime series."
            },
            "judicial_focus": [
                "storytelling quality",
                "character development",
                "world-building"
            ],
            "session_id": "test-session-123",
            "max_rounds": 2
        },
        "clarification_needed": False,
        "clarification_response": None,
        "current_round": 1,
        "max_rounds": 2,
        "debate_history": [],
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
        "truth_report": None,
        "final_verdict": None,
        "winner": None
    }

    print("Strategist is formulating the battle plan...\n")

    try:
        result = strategist_node_a(state)

        strategy_json = result.get("team_a_strategy")

        if strategy_json:
            strategy_dict = json.loads(strategy_json)
            print("[STRATEGY GENERATED]\n")
            print(json.dumps(strategy_dict, indent=2))
        else:
            print("Failed to generate strategy.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()