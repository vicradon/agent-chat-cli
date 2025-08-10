from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from config.cli_config import config

general_model = GoogleModel(
    config.gemini_model,
    provider=GoogleProvider(api_key=config.gemini_api_key),
)

