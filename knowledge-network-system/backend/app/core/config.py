from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Knowledge Network API"
    app_env: str = "dev"
    app_debug: bool = True

    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"

    database_url: str = "sqlite:///./app.db"
    upload_dir: str = "../data/raw_uploads"
    parsed_dir: str = "../data/parsed"
    graph_dir: str = "../data/graphs"

    # Optional LLM settings (OpenAI-compatible APIs, including Qwen endpoints that expose /v1/chat/completions).
    llm_enabled: bool = False
    llm_provider: str = "openai_compatible"
    # Read from .env, supporting both generic names (BASE_URL/API_KEY) and LLM-prefixed names.
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "BASE_URL"),
    )
    llm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("LLM_API_KEY", "API_KEY", "OPENAI_API_KEY"),
    )
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 1400

    class Config:
        env_file = "../.env"
        case_sensitive = False


settings = Settings()
