"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database - Required
    DATABASE_URL: str = Field(..., description="Database connection string")
    
    # Security - Required
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    
    # OpenAI - Required
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL_NAME: str = Field(..., description="OpenAI model name")
    EMBEDDING_MODEL_NAME: str = Field(..., description="OpenAI embedding model name")
    
    # ChromaDB - Required
    CHROMA_PERSIST_DIR: str = Field(..., description="ChromaDB persist directory")
    CHROMA_COLLECTION_NAME: str = Field(..., description="ChromaDB collection name")
    CHUNK_SIZE: int = Field(..., description="Text chunk size")
    CHUNK_OVERLAP: int = Field(..., description="Text chunk overlap")
    
    # File paths - Required
    HR_POLICIES_PATH: str = Field(..., description="Path to HR policies PDF")
    
    # Optional
    DEBUG: bool = Field(default=False, description="Debug mode")


settings = Settings()
