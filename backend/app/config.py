import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Tone Checker (VibeCheck)"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tone_checker.db")
    
    # Toxicity thresholds (percentages)
    SAFE_THRESHOLD: float = 30.0
    CAUTION_THRESHOLD: float = 60.0
    MAX_TEXT_LENGTH: int = 1000

    # ML parameters
    SIMILARITY_FLOOR: float = 0.60
    MODEL_FALLBACK: str = "unitary/toxic-bert"

settings = Settings()

