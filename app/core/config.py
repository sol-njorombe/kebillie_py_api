from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACTIVE_EMBEDDING_MODEL: str = "jina"
    JINA_MIN_SEARCH_SIMILARITY: float = 0.5
    GEMMA_MIN_SEARCH_SIMILARITY: float = 0.5

    class Config:
        env_file = ".env"

settings = Settings()
