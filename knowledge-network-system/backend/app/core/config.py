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

    class Config:
        env_file = "../.env"
        case_sensitive = False


settings = Settings()
