import json
from backend.agents.dispatcher import dispatcher_node


def main():
    print("==================================================")
    print("⚔️  STOA DISPATCHER TEST ARENA ⚔️")
    print("Type 'exit' or 'quit' to end the session.")
    print("==================================================\n")

    # Initialize a mock state
    state = {
        "user_query": "",
        "clarification_response": None
    }

    while True:
        user_input = input("👤 You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting Arena. Goodbye!")
            break

        if not user_input:
            continue

        # Update state with the user's latest input
        state["user_query"] = user_input

        print("🤖 Dispatcher is thinking...\n")

        try:
            # Run the node
            result = dispatcher_node(state)

            # Check the routing decision
            if result.get("clarification_needed"):
                print("⚠️  [CLARIFICATION REQUESTED]")
                print(f"Dispatcher: {result.get('clarification_response')}\n")

                # Save the clarification response to state so the LLM remembers it next turn
                state["clarification_response"] = result.get("clarification_response")
            else:
                print("✅  [MANIFEST GENERATED]")
                # Pretty-print the manifest
                print(json.dumps(result.get("arena_manifest"), indent=2))
                print("\n" + "=" * 50 + "\n")

                # Reset clarification state after a successful manifest generation
                state["clarification_response"] = None

        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()