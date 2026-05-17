import json
from backend.agents.dispatcher import dispatcher_node


def main():
    print("==================================================")
    print("STOA DISPATCHER TEST ARENA")
    print("Type 'exit' or 'quit' to end the session.")
    print("==================================================\n")

    state = {
        "user_query": "",
        "clarification_response": None
    }

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting Arena. Goodbye!")
            break

        if not user_input:
            continue

        state["user_query"] = user_input

        print("Dispatcher is thinking...\n")

        try:
            result = dispatcher_node(state)

            if result.get("clarification_needed"):
                print("[CLARIFICATION REQUESTED]")
                print(f"Dispatcher: {result.get('clarification_response')}\n")

                state["clarification_response"] = result.get("clarification_response")
            else:
                print("[MANIFEST GENERATED]")
                print(json.dumps(result.get("arena_manifest"), indent=2))
                print("\n" + "=" * 50 + "\n")

                state["clarification_response"] = None

        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()