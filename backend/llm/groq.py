from langchain_groq import ChatGroq
from backend.config import settings

# For the Dispatcher: Low temperature (0.3) for strict JSON routing
dispatcher_llm = ChatGroq(
    model=settings.GROQ_LLM_MODEL,  # e.g., llama-3.3-70b-versatile
    api_key=settings.GROQ_API_KEY,
    temperature=0.3
)

# For the Teams (Strategist, Researcher, Critic, Speaker):
# Higher temperature (0.7) for creative, persuasive arguments
team_llm = ChatGroq(
    model=settings.GROQ_LLM_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.7
)