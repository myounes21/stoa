import json
from backend.agents.dispatcher import dispatcher_node
from backend.models.state import STOAState

def main():
    print("=" * 50)
    print("STOA DISPATCHER TEST")
    print("=" * 50)

    print("\nTEST 1: Clear query (expecting no clarification)")
    print("-" * 40)

    state_clear: STOAState = {
        "user_query": "one piece vs attack on titan",
        "arena_manifest": None,
        "clarification_needed": None,
        "clarification_response": None,
        "current_round": 0,
        "max_rounds": 2,
        "teams": {
            "A": {
                "strategy": None,
                "evidence": None,
                "critic_status": None,
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
        "debate_history": [],
        "truth_report": None,
        "final_verdict": None,
        "winner": None,
    }

    try:
        result = dispatcher_node(state_clear)
        print(f"Clarification needed : {result.get('clarification_needed')}")
        print(f"Clarification response: {result.get('clarification_response')}")
        manifest = result.get("arena_manifest")
        if manifest:
            print("\nArena Manifest generated:")
            print(json.dumps(manifest, indent=2))
        else:
            print("No manifest generated.")
    except Exception as e:
        print(f"Error: {e}")
        raise

    print("\nTEST 2: Ambiguous query (expecting clarification)")
    print("-" * 40)

    state_ambiguous: STOAState = {
        **state_clear,
        "user_query": "what is the best anime?"
    }

    try:
        result = dispatcher_node(state_ambiguous)
        print(f"Clarification needed : {result.get('clarification_needed')}")
        print(f"Clarification response: {result.get('clarification_response')}")
        manifest = result.get("arena_manifest")
        if manifest:
            print("\nManifest generated (unexpected):")
            print(json.dumps(manifest, indent=2))
        else:
            print("No manifest - correct behavior.")
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()