import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.graph import stoa_graph
from backend.models.state import STOAState

websocket_router = APIRouter()


def _build_initial_state(query: str) -> STOAState:
    return {
        "user_query": query,
        "arena_manifest": None,
        "clarification_needed": None,
        "clarification_response": None,
        "current_round": 1,
        "max_rounds": 2,
        "debate_history": [],
        "team_a_strategy": None,
        "team_a_evidence": None,
        "team_a_critic_status": None,
        "team_a_critic_decision": None,
        "team_a_retry_count": 0,
        "team_a_weakness_flag": False,
        "team_a_argument": None,
        "team_b_strategy": None,
        "team_b_evidence": None,
        "team_b_critic_status": None,
        "team_b_critic_decision": None,
        "team_b_retry_count": 0,
        "team_b_weakness_flag": False,
        "team_b_argument": None,
        "truth_report": None,
        "final_verdict": None,
        "winner": None,
    }


def _format_node_update(node_name: str, output: dict) -> dict | None:
    """Map a LangGraph node output to a typed WebSocket message."""

    if node_name == "dispatcher":
        manifest = output.get("arena_manifest")
        if manifest:
            return {
                "type": "arena_ready",
                "data": {
                    "topic": manifest.get("topic"),
                    "team_a": manifest.get("team_a", {}).get("team_name"),
                    "team_b": manifest.get("team_b", {}).get("team_name"),
                }
            }
        if output.get("clarification_needed"):
            return {
                "type": "clarification_needed",
                "data": {"message": "Please provide two specific options to debate."}
            }

    if node_name in ("strategist_a", "strategist_b"):
        strategy = output.get("team_a_strategy") or output.get("team_b_strategy")
        team = "A" if node_name == "strategist_a" else "B"
        if strategy:
            return {
                "type": "agent_output",
                "data": {"team": team, "agent": "Strategist", "content": strategy}
            }

    if node_name in ("researcher_a", "researcher_b"):
        evidence = output.get("team_a_evidence") or output.get("team_b_evidence")
        team = "A" if node_name == "researcher_a" else "B"
        if evidence:
            return {
                "type": "agent_output",
                "data": {"team": team, "agent": "Researcher", "content": evidence}
            }

    if node_name in ("critic_a", "critic_b"):
        decision = output.get("team_a_critic_decision") or output.get("team_b_critic_decision")
        status = output.get("team_a_critic_status") or output.get("team_b_critic_status")
        team = "A" if node_name == "critic_a" else "B"
        if decision:
            return {
                "type": "agent_output",
                "data": {"team": team, "agent": "Critic", "content": decision, "status": status}
            }

    if node_name in ("speaker_a", "speaker_b"):
        argument = output.get("team_a_argument") or output.get("team_b_argument")
        team = "A" if node_name == "speaker_a" else "B"
        if argument:
            return {
                "type": "argument",
                "data": {"team": team, "content": argument}
            }

    if node_name == "collect_round":
        history = output.get("debate_history", [])
        return {
            "type": "round_complete",
            "data": {"round": len(history)}
        }

    if node_name == "clerk":
        truth_report = output.get("truth_report")
        if truth_report:
            return {
                "type": "truth_report",
                "data": json.loads(truth_report)
            }

    if node_name == "analyst":
        final_verdict = output.get("final_verdict")
        if final_verdict:
            return {
                "type": "verdict",
                "data": {
                    "winner": output.get("winner"),
                    **json.loads(final_verdict)
                }
            }

    return None


@websocket_router.websocket("/ws/debate")
async def debate_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        data = await websocket.receive_json()
        query = data.get("query", "").strip()

        if not query:
            await websocket.send_json({
                "type": "error",
                "message": "No query provided."
            })
            return

        initial_state = _build_initial_state(query)

        async for update in stoa_graph.astream(
            initial_state,
            stream_mode="updates"
        ):
            for node_name, node_output in update.items():
                message = _format_node_update(node_name, node_output)
                if message:
                    await websocket.send_json(message)

        await websocket.send_json({"type": "complete"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})