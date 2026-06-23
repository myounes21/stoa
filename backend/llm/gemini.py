from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

judge_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_LLM_MODEL,
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.3
)
