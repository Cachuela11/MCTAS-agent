from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"
    time_limit_sec: int = 10
    memory_limit_mb: int = 256

    model_config = {"env_prefix": ""}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
