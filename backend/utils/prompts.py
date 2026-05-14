import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(file: str, key: str) -> dict:
    with open(PROMPTS_DIR / file) as f:
        return yaml.safe_load(f)[key]