from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.config import settings
from backend.models.schemas import ArenaManifest, TeamMission
from backend.models.state import STOAState


llm = ChatGroq(
    model=settings.GROQ_LLM_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.3
)

structured_llm = llm.with_structured_output(ArenaManifest)

DISPATCHER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the STOA Dispatcher. Your job is to analyze a user query and extract two opposing debate positions.

Given a query, produce an ArenaManifest with:
- A clear topic
- Team A with a name, stance, and mission goal
- Team B with a name, stance, and mission goal

Both teams must have clearly opposing positions. Be specific and aggressive in defining each team's stance and mission goal."""),
    ("human", "{query}")
])

dispatcher_chain = DISPATCHER_PROMPT | structured_llm


def needs_clarification(query: str) -> bool:
    """Check if the query is too vague to extract two positions."""
    vague_indicators = len(query.split()) < 4
    return vague_indicators


def dispatcher_node(state: STOAState) -> dict:
    query = state["user_query"]

    if state.get("clarification_response"):
        query = f"{query} — clarification: {state['clarification_response']}"

    if needs_clarification(query) and not state.get("clarification_response"):
        return {
            "clarification_needed": True,
            "clarification_response": None
        }

    manifest = dispatcher_chain.invoke({"query": query})

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