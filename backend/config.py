from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


ENV_PATH = Path(__file__).resolve().parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")


    GROQ_API_KEY : str
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile" #llama-3.1-8b-instant #llama-3.3-70b-versatile

    GEMINI_API_KEY: str
    GEMINI_LLM_MODEL: str = "gemini-3.5-flash"

    TAVILY_API_KEY: str

    MAX_ROUNDS: int = 2
    TAVILY_MAX_RESULTS: int = 2





settings = Settings()
