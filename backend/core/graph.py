from langgraph.graph import StateGraph, START, END

from backend.models.state import STOAState
from backend.agents.dispatcher import dispatcher_node
from backend.agents.team.strategist import strategist_node_a, strategist_node_b
from backend.agents.team.researcher import researcher_node_a, researcher_node_b
from backend.agents.team.critic import critic_node_a, critic_router_a, critic_node_b, critic_router_b
from backend.agents.team.speaker import speaker_node_a, speaker_node_b


def dispatcher_router(state: STOAState) -> list[str]:
    if state["clarification_needed"]:
        return [END]
    return ["strategist_a", "strategist_b"]


def build_graph():
    graph = StateGraph(STOAState)

    # --- Register Nodes ---
    graph.add_node("dispatcher", dispatcher_node)
    graph.add_node("strategist_a", strategist_node_a)
    graph.add_node("strategist_b", strategist_node_b)
    graph.add_node("researcher_a", researcher_node_a)
    graph.add_node("researcher_b", researcher_node_b)
    graph.add_node("critic_a", critic_node_a)
    graph.add_node("critic_b", critic_node_b)
    graph.add_node("speaker_a", speaker_node_a)
    graph.add_node("speaker_b", speaker_node_b)

    # --- Wire Edges ---
    graph.add_edge(START, "dispatcher")

    # Fan-out: dispatcher → both teams simultaneously
    graph.add_conditional_edges(
        "dispatcher",
        dispatcher_router,
        {
            END: END,
            "strategist_a": "strategist_a",
            "strategist_b": "strategist_b"
        }
    )

    # Team A flow
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

    # Team B flow
    graph.add_edge("strategist_b", "researcher_b")
    graph.add_edge("researcher_b", "critic_b")
    graph.add_conditional_edges(
        "critic_b",
        critic_router_b,
        {
            "speaker_b": "speaker_b",
            "researcher_b": "researcher_b"
        }
    )

    # Fan-in: both speakers → END
    graph.add_edge("speaker_a", END)
    graph.add_edge("speaker_b", END)

    return graph.compile()


stoa_graph = build_graph()