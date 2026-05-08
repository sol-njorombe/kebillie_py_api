from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACTIVE_EMBEDDING_MODEL: str = "jina"

    class Config:
        env_file = ".env"

settings = Settings()
