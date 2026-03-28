"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/hr_assistant_db?options=-csearch_path%3Dhr_assistant,public"
    SECRET_KEY: str = "change-me-in-production"
    OPENAI_API_KEY: str = ""
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    HR_POLICIES_PATH: str = "../hr_policies/hr_policies.pdf"
    DEBUG: bool = True


settings = Settings()
