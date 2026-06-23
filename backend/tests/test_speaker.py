import json
from backend.models.schemas import CriticDecision
from backend.models.state import STOAState
from backend.agents.team.speaker import make_speaker

def main():
    print("=" * 50)
    print("STOA SPEAKER TEST: TEAM A (ONE PIECE)")
    print("=" * 50)

    mock_strategy = {
        "win_condition": "Prove that One Piece surpasses Attack on Titan in storytelling, character development, and world-building",
        "core_claims": [
            "One Piece has a more diverse and developed cast of characters",
            "One Piece's world-building is more expansive and immersive",
            "One Piece's episodic structure feeds into a richer larger narrative"
        ],
        "anticipated_attacks": [
            "ATTACK: Attack on Titan has darker, more mature themes | COUNTER: Maturity is not depth - One Piece's 1000+ chapters of interconnected lore demonstrates far greater narrative complexity",
            "ATTACK: Attack on Titan has a more focused plot | COUNTER: Focus at the cost of world richness is a limitation, not a strength"
        ],
        "research_directives": []
    }

    mock_evidence = {
        "research_summary": "One Piece has rich world-building with hundreds of named characters and complex lore including the Void Century.",
        "evidence_list": [
            {
                "claim": "One Piece has a large cast of named characters",
                "source_url": "https://en.wikipedia.org/wiki/List_of_One_Piece_characters",
                "raw_snippet": "The series features a vast array of characters including the Straw Hat Pirates, the Four Emperors, and the World Government with hundreds of named individuals.",
                "extracted_fact": "One Piece features hundreds of named characters across multiple factions including the Straw Hat Pirates, Four Emperors, and the World Government."
            },
            {
                "claim": "The Void Century adds narrative depth",
                "source_url": "https://onepiece.fandom.com/wiki/Void_Century",
                "raw_snippet": "The Void Century is a 100-year period of history that has been erased from the world's records, connected to the Will of D. and the Ancient Weapons.",
                "extracted_fact": "The Void Century is a deliberately erased 100-year period connected to the Will of D. and Ancient Weapons, adding deep historical mystery to the world."
            }
        ],
        "failed_searches": []
    }

    base_state: STOAState = {
        "user_query": "which is better one piece or attack on titan",
        "arena_manifest": {
            "topic": "One Piece vs Attack on Titan",
            "team_a": {
                "team_name": "Team One Piece",
                "stance": "One Piece is the better anime series.",
                "mission_goal": "Prove that One Piece's world-building, characters, and storytelling make it the superior anime."
            },
            "team_b": {
                "team_name": "Team Attack on Titan",
                "stance": "Attack on Titan is the better anime series.",
                "mission_goal": "Prove Attack on Titan's dark storytelling makes it superior."
            },
            "judicial_focus": ["storytelling quality", "character development", "world-building"],
            "session_id": "test-session-123",
            "max_rounds": 2
        },
        "clarification_needed": False,
        "clarification_response": None,
        "current_round": 1,
        "max_rounds": 2,
        "debate_history": [],
        "teams": {
            "A": {
                "strategy": json.dumps(mock_strategy),
                "evidence": json.dumps(mock_evidence),
                "critic_status": "APPROVED",
                "critic_decision": None,
                "retry_count": 0,
                "weakness_flag": False,
                "argument": None
            },
            "B": {
                "strategy": None,
                "evidence": None,
                "critic_status": None,
                "critic_decision": None,
                "retry_count": 0,
                "weakness_flag": False,
                "argument": None
            }
        },
        "truth_report": None,
        "final_verdict": None,
        "winner": None
    }

    print("\nTEST 1: No Critic weak points (baseline)")
    print("-" * 40)
    try:
        result = make_speaker("A")(base_state)
        argument = result.get("teams", {}).get("A", {}).get("argument")
        if argument:
            print("\n[TEAM A ARGUMENT]\n")
            print(argument)
        else:
            print("No argument produced.")
    except Exception as e:
        print(f"Error: {e}")
        raise

    print("\nTEST 2: With Critic weak points")
    print("-" * 40)
    mock_critic_decision = CriticDecision(
        status="APPROVED",
        reasoning="Evidence is mostly solid.",
        weak_points=[
            "No direct evidence comparing character count to Attack on Titan",
            "Void Century claim lacks a primary academic source"
        ],
        retry_directive=None
    )

    state_with_weakpoints: STOAState = {
        **base_state,
        "teams": {
            "A": {
                **base_state["teams"]["A"],
                "critic_decision": mock_critic_decision.model_dump_json()
            },
            "B": base_state["teams"]["B"]
        }
    }

    try:
        result = make_speaker("A")(state_with_weakpoints)
        argument = result.get("teams", {}).get("A", {}).get("argument")
        if argument:
            print("\n[TEAM A ARGUMENT - WITH WEAK POINTS]\n")
            print(argument)
        else:
            print("No argument produced.")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()