from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME:str = "youtube-rag"
    ENV:str="dev"
    DEBUG:bool=True

    API_V1_PREFIX:str="/api/v1"
    DATABASE_URL:str
    VERIFICATION_SECRET_KEY:str
    CLIENT_BASE_URL:str
    EMAIL_ADDRESS:str
    EMAIL_PASSWORD:str
    LLM_API_KEY:str
    LLM_MODEL_NAME:str

    REDIS_HOST:str
    REDIS_PORT:int

    ACCESS_TOKEN_SECRET:str
    REFRESH_TOKEN_SECRET:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60 * 10

    QDRANT_HOST:str
    QDRANT_PORT:int
    QDRANT_COLLECTION:str
    SPARSE_EMBEDDING_MODEL:str

    DENSE_EMBEDDING_MODEL:str

    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=True,
    )

settings = Settings()