from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from openai.types.responses import WebSearchToolParam 
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

from config.cli_config import config

gemini_model = GoogleModel(
    config.gemini_model,
    provider=GoogleProvider(api_key=config.gemini_api_key),
)

openrouter_model = OpenAIModel(
    config.openrouter_model_name,
    provider=OpenRouterProvider(api_key=config.openrouter_api_key),
)

openai_model_settings = OpenAIResponsesModelSettings(
    openai_builtin_tools=[WebSearchToolParam(type='web_search_preview')],
)