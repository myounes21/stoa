import json
from backend.models.state import STOAState
from backend.agents.team.researcher import researcher_node_a


def main():
    print("==================================================")
    print("STOA RESEARCHER TEST: TEAM A (ONE PIECE)")
    print("==================================================\n")

    mock_strategy = {
        "win_condition": "Prove that One Piece's superior character development and world-building make it the better anime series, as evidenced by its ability to craft compelling characters and a rich, immersive world that resonates with audiences",
        "core_claims": [
            "One Piece's diverse and well-developed cast of characters is unparalleled in anime",
            "One Piece's world-building is more immersive and expansive, with a rich history and lore"
        ],
        "anticipated_attacks": [
            "Attack on Titan's darker and more mature themes will resonate more with audiences",
            "Attack on Titan's plot is more cohesive and well-structured"
        ],
        "research_directives": [
            "Find data on the number of unique characters in One Piece vs Attack on Titan",
            "Gather examples of One Piece's world-building, such as the Will of D. and the Void Century"
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


if __name__ == "__main__":
    main()