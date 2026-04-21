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
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 1400

    class Config:
        env_file = "../.env"
        case_sensitive = False


settings = Settings()
