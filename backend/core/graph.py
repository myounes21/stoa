from langgraph.graph import StateGraph, START, END

from backend.models.state import STOAState
from backend.agents.dispatcher import dispatcher_node
from backend.agents.team.strategist import make_strategist
from backend.agents.team.researcher import make_researcher
from backend.agents.team.critic import make_critic, make_critic_router
from backend.agents.team.speaker import make_speaker
from backend.agents.judges.clerk import clerk_node
from backend.agents.judges.analyst import analyst_node


def dispatcher_router(state: STOAState) -> list[str]:
    if state["clarification_needed"]:
        return [END]
    return ["strategist_a", "strategist_b"]


def collect_round(state: STOAState) -> dict:
    """Fan-in node: appends round results to history and resets team state."""
    round_entry = {
        "round": state["current_round"],
        "team_a": state.get("teams", {}).get("A", {}).get("argument"),
        "team_b": state.get("teams", {}).get("B", {}).get("argument")
    }

    updated_history = state["debate_history"] + [round_entry]

    print(f"\n[Round {state['current_round']}] Arguments collected. Resetting for next round.")

    return {
        "current_round": state["current_round"] + 1,
        "debate_history": updated_history,
        "teams": {
            "A": {
                "strategy": None,
                "evidence": None,
                "argument": None,
                "critic_status": None,
                "critic_decision": None,
                "retry_count": 0,
                "weakness_flag": False,
            },
            "B": {
                "strategy": None,
                "evidence": None,
                "argument": None,
                "critic_status": None,
                "critic_decision": None,
                "retry_count": 0,
                "weakness_flag": False,
            }
        }
    }


def round_router(state: STOAState) -> list[str]:
    """Route to next round or Judge panel."""
    if state["current_round"] <= state["max_rounds"]:
        return ["strategist_a", "strategist_b"]
    return ["clerk"]


def build_graph():
    graph = StateGraph(STOAState)

    graph.add_node("dispatcher", dispatcher_node)
    graph.add_node("strategist_a", make_strategist("A"))
    graph.add_node("strategist_b", make_strategist("B"))
    graph.add_node("researcher_a", make_researcher("A"))
    graph.add_node("researcher_b", make_researcher("B"))
    graph.add_node("critic_a", make_critic("A"))
    graph.add_node("critic_b", make_critic("B"))
    graph.add_node("speaker_a", make_speaker("A"))
    graph.add_node("speaker_b", make_speaker("B"))
    graph.add_node("collect_round", collect_round)
    graph.add_node("clerk", clerk_node)
    graph.add_node("analyst", analyst_node)

    graph.add_edge(START, "dispatcher")

    graph.add_conditional_edges(
        "dispatcher",
        dispatcher_router,
        {
            END: END,
            "strategist_a": "strategist_a",
            "strategist_b": "strategist_b"
        }
    )

    graph.add_edge("strategist_a", "researcher_a")
    graph.add_edge("researcher_a", "critic_a")
    graph.add_conditional_edges(
        "critic_a",
        make_critic_router("A"),
        {
            "speaker_a": "speaker_a",
            "researcher_a": "researcher_a"
        }
    )

    graph.add_edge("strategist_b", "researcher_b")
    graph.add_edge("researcher_b", "critic_b")
    graph.add_conditional_edges(
        "critic_b",
        make_critic_router("B"),
        {
            "speaker_b": "speaker_b",
            "researcher_b": "researcher_b"
        }
    )

    graph.add_edge(["speaker_a", "speaker_b"], "collect_round")

    graph.add_conditional_edges(
        "collect_round",
        round_router,
        {
            "strategist_a": "strategist_a",
            "strategist_b": "strategist_b",
            "clerk": "clerk"
        }
    )

    graph.add_edge("clerk", "analyst")
    graph.add_edge("analyst", END)

    return graph.compile()


stoa_graph = build_graph()
