import sys
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str 
    gemini_model: str = "gemini-2.5-flash"
    sqlite_db_name: str = "database.db"

    model_config = SettingsConfigDict(
        env_file=".env"
    )


def create_config() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        missing = [
            err["loc"][0].upper()
            for err in e.errors()
            if err["type"] == "missing"
        ]
        print(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)


config = create_config()