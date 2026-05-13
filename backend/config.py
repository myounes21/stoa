from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


ENV_PATH = Path(__file__).resolve().parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")


    GROQ_API_KEY : str
    GROQ_LLM_MODEL: str = "llama-3.3-70b-versatile"

    GEMINI_API_KEY: str
    GEMINI_LLM_MODEL: str = "gemini-2.5-pro"




settings = Settings()
