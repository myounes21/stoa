import json
from backend.models.state import STOAState
from backend.agents.team.critic import critic_node_a


def main():
    print("=" * 50)
    print("STOA CRITIC TEST: TEAM A (ONE PIECE)")
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

    mock_evidence = {
        "research_summary": "One Piece has a vast array of characters, a unique power system with Devil Fruits and Haki, and a rich lore with the Void Century and Will of D mystery. Attack on Titan has a more concise cast of characters and a different approach to storytelling.",
        "evidence_list": [
            {
                "claim": "One Piece has a large cast of characters",
                "source_url": "https://www.youtube.com/watch?v=r0FFS1NbDRw",
                "raw_snippet": "One piece has one of the largest Castle characters in all of anime, if not all of entertainment spanning over 35 plus characters that everyone can name off the top of their head",
                "extracted_fact": "One piece has one of the largest Castle characters in all of anime, if not all of entertainment spanning over 35 plus characters that everyone can name off the top of their head"
            },
            {
                "claim": "Attack on Titan has a more concise cast of characters",
                "source_url": "https://www.youtube.com/watch?v=r0FFS1NbDRw",
                "raw_snippet": "attack on Titan on the other end, that's one of the most concise cast of characters",
                "extracted_fact": "attack on Titan on the other end, that's one of the most concise cast of characters"
            },
            {
                "claim": "One Piece has a unique power system with Devil Fruits",
                "source_url": "https://www.youtube.com/watch?v=3ZcpOHEKC9c",
                "raw_snippet": "Devil fruits and the secrets of these legendary fruits are one of the true Mysteries remaining in the story so let's explain exactly how this power system works",
                "extracted_fact": "Devil fruits and the secrets of these legendary fruits are one of the true Mysteries remaining in the story so let's explain exactly how this power system works"
            },
            {
                "claim": "One Piece has a rich lore with the Void Century and Will of D mystery",
                "source_url": "https://www.slashfilm.com/2119009/will-of-d-netflix-one-piece-season-2-explained/",
                "raw_snippet": "The origin of the Clan of D goes all the way back to the fateful Great War during the Void Century",
                "extracted_fact": "The origin of the Clan of D goes all the way back to the fateful Great War during the Void Century"
            },
            {
                "claim": "The Will of D is a form of inherited will",
                "source_url": "https://www.slashfilm.com/2119009/will-of-d-netflix-one-piece-season-2-explained/",
                "raw_snippet": "We don't know everything about the Will of D or its full purpose, but we do know it is a form of inherited will, specifically surrounding those of the Clan of D",
                "extracted_fact": "We don't know everything about the Will of D or its full purpose, but we do know it is a form of inherited will, specifically surrounding those of the Clan of D"
            }
        ],
        "failed_searches": []
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
        "team_a_evidence": json.dumps(mock_evidence),
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

    print("Critic is auditing the evidence...\n")

    try:
        result = critic_node_a(state)

        print(f"Critic Status : {result.get('team_a_critic_status')}")
        print(f"Retry Count   : {result.get('team_a_retry_count')}")
        print(f"Weakness Flag : {result.get('team_a_weakness_flag')}")
        print(f"\nFull Decision:\n")

        decision_json = result.get("team_a_critic_decision")
        if decision_json:
            print(json.dumps(json.loads(decision_json), indent=2))

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()