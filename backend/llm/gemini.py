from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

# For the Judges (Clerk, Analyst):
# Low temperature (0.3) because we want strict, consistent evaluation
judge_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_LLM_MODEL,
    api_key=settings.GEMINI_API_KEY,
    temperature=0.3
)