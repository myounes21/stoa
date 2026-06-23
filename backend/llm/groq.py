from langchain_groq import ChatGroq
from backend.config import settings

dispatcher_llm = ChatGroq(
    model=settings.GROQ_LLM_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,
    max_retries=6
)

team_llm = ChatGroq(
    model=settings.GROQ_LLM_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.7,
    max_retries=6
)