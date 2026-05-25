from langchain_core.prompts import ChatPromptTemplate

from backend.config import settings
from backend.models.schemas import ArenaManifest, DispatcherOutput
from backend.models.state import STOAState
from backend.utils.prompts import load_prompt

from backend.llm.groq import dispatcher_llm

_prompt = load_prompt("dispatcher.yaml", "dispatcher")

structured_llm = dispatcher_llm.with_structured_output(DispatcherOutput)

DISPATCHER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", _prompt["system"]),
    ("human", _prompt["human"])
])

dispatcher_chain = DISPATCHER_PROMPT | structured_llm

def dispatcher_node(state: STOAState) -> dict:
    query = state["user_query"]

    llm_output: DispatcherOutput = dispatcher_chain.invoke({"query": query})

    if llm_output.clarification_needed or not llm_output.manifest:
        return {
            "clarification_needed": True,
            "clarification_response": llm_output.clarification_response,
            "user_query": state["user_query"]
        }

    manifest = ArenaManifest(**llm_output.manifest.model_dump())

    return {
        "clarification_needed": False,
        "arena_manifest": manifest.model_dump(),
        "current_round": 1,
        "max_rounds": settings.MAX_ROUNDS,
        "debate_history": [],
        "team_a_retry_count": 0,
        "team_b_retry_count": 0,
        "team_a_weakness_flag": False,
        "team_b_weakness_flag": False,
    }