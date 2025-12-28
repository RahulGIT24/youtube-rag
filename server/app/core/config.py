from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME:str = "youtube-rag"
    ENV:str="dev"
    DEBUG:bool=True

    API_V1_PREFIX:str="/api/v1"

    REDIS_HOST:str
    REDIS_PORT:int

    JWT_SECRET:str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    QDRANT_HOST:str
    QDRANT_PORT:int
    QDRANT_COLLECTION:str

    DENSE_EMBEDDING_MODEL:str

    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True
    )

settings = Settings()