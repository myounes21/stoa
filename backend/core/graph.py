from langgraph.graph import StateGraph, START, END

from backend.models.state import STOAState
from backend.agents.dispatcher import dispatcher_node
from backend.agents.team.strategist import strategist_node_a, strategist_node_b
from backend.agents.team.researcher import researcher_node_a, researcher_node_b
from backend.agents.team.critic import critic_node_a, critic_router_a, critic_node_b, critic_router_b
from backend.agents.team.speaker import speaker_node_a, speaker_node_b
from backend.agents.judges.clerk import clerk_node


def dispatcher_router(state: STOAState) -> list[str]:
    if state["clarification_needed"]:
        return [END]
    return ["strategist_a", "strategist_b"]


def collect_round(state: STOAState) -> dict:
    """Fan-in node: appends round results to history and resets team state."""
    round_entry = {
        "round": state["current_round"],
        "team_a": state["team_a_argument"],
        "team_b": state["team_b_argument"]
    }

    updated_history = state["debate_history"] + [round_entry]

    print(f"\n[Round {state['current_round']}] Arguments collected. Resetting for next round.")

    return {
        "current_round": state["current_round"] + 1,
        "debate_history": updated_history,
        "team_a_strategy": None,
        "team_a_evidence": None,
        "team_a_argument": None,
        "team_a_critic_status": None,
        "team_a_critic_decision": None,
        "team_a_retry_count": 0,
        "team_a_weakness_flag": False,
        "team_b_strategy": None,
        "team_b_evidence": None,
        "team_b_argument": None,
        "team_b_critic_status": None,
        "team_b_critic_decision": None,
        "team_b_retry_count": 0,
        "team_b_weakness_flag": False,
    }


def round_router(state: STOAState) -> list[str]:
    """Route to next round or Judge panel."""
    if state["current_round"] <= state["max_rounds"]:
        return ["strategist_a", "strategist_b"]
    return ["clerk"]


def build_graph():
    graph = StateGraph(STOAState)

    # Register Nodes
    graph.add_node("dispatcher", dispatcher_node)
    graph.add_node("strategist_a", strategist_node_a)
    graph.add_node("strategist_b", strategist_node_b)
    graph.add_node("researcher_a", researcher_node_a)
    graph.add_node("researcher_b", researcher_node_b)
    graph.add_node("critic_a", critic_node_a)
    graph.add_node("critic_b", critic_node_b)
    graph.add_node("speaker_a", speaker_node_a)
    graph.add_node("speaker_b", speaker_node_b)
    graph.add_node("collect_round", collect_round)
    graph.add_node("clerk", clerk_node)

    #  Wire Edges
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

    # Fan-in: both speakers → collect_round
    graph.add_edge("speaker_a", "collect_round")
    graph.add_edge("speaker_b", "collect_round")

    # Round router: loop back or Judge panel
    graph.add_conditional_edges(
        "collect_round",
        round_router,
        {
            "strategist_a": "strategist_a",
            "strategist_b": "strategist_b",
            "clerk": "clerk"
        }
    )

    # Clerk → END (temporary until Analyst is built)
    graph.add_edge("clerk", END)

    return graph.compile()


stoa_graph = build_graph()