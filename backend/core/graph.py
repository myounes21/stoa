from langgraph.graph import StateGraph, START, END

from backend.models.state import STOAState
from backend.agents.dispatcher import dispatcher_node
from backend.agents.team.strategist import strategist_node_a
from backend.agents.team.researcher import researcher_node_a
from backend.agents.team.critic import critic_node_a, critic_router_a
from backend.agents.team.speaker import speaker_node_a


def dispatcher_router(state: STOAState) -> str:
    if state["clarification_needed"]:
        return END
    return "strategist_a"


def build_graph():
    graph = StateGraph(STOAState)

    # --- Register Nodes ---
    graph.add_node("dispatcher", dispatcher_node)
    graph.add_node("strategist_a", strategist_node_a)
    graph.add_node("researcher_a", researcher_node_a)
    graph.add_node("critic_a", critic_node_a)
    graph.add_node("speaker_a", speaker_node_a)

    # --- Wire Edges ---
    graph.add_edge(START, "dispatcher")

    graph.add_conditional_edges(
        "dispatcher",
        dispatcher_router,
        {
            END: END,
            "strategist_a": "strategist_a"
        }
    )

    graph.add_edge("strategist_a", "researcher_a")
    graph.add_edge("researcher_a", "critic_a")

    graph.add_conditional_edges(
        "critic_a",
        critic_router_a,
        {
            "speaker_a": "speaker_a",
            "researcher_a": "researcher_a"
        }
    )

    graph.add_edge("speaker_a", END)

    return graph.compile()


stoa_graph = build_graph()