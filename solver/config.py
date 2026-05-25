from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    time_limit_sec: int = 10
    memory_limit_mb: int = 256

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="")


settings = Settings()
