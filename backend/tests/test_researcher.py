import json
from backend.models.state import STOAState
from backend.agents.team.researcher import researcher_node_a


def main():
    print("=" * 50)
    print("STOA RESEARCHER TEST: TEAM A (ONE PIECE)")
    print("=" * 50 + "\n")

    mock_strategy = {
        "win_condition": "Prove that One Piece's superior character development and world-building make it the better anime series.",
        "core_claims": [
            "One Piece has a larger named character roster with individually developed backstories",
            "One Piece's world-building mechanics (Devil Fruits, Haki, Void Century) are more layered than AOT's"
        ],
        "anticipated_attacks": [
            "ATTACK: Attack on Titan has a tighter, more cohesive plot | COUNTER: One Piece's longer runtime allows deeper world exploration",
            "ATTACK: AOT's themes are more mature and impactful | COUNTER: One Piece tackles themes of freedom, justice, and sacrifice at equal depth"
        ],
        "research_directives": [
            "One Piece total named characters count vs Attack on Titan",
            "One Piece Devil Fruit types and Haki system explained",
            "One Piece Void Century lore and Will of D mystery"
        ]
    }

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
        "team_a_strategy": json.dumps(mock_strategy),
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
        "winner": None
    }

    print("Researcher is executing Tavily searches and compiling evidence...\n")

    try:
        result = researcher_node_a(state)
        evidence_json = result.get("team_a_evidence")

        if evidence_json:
            evidence_dict = json.loads(evidence_json)
            print("[EVIDENCE GATHERED]\n")
            print(json.dumps(evidence_dict, indent=2))
        else:
            print("Failed to gather evidence.")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()