from src.providers.base import AIProvider
from src.providers.openrouter import OpenRouterProvider
from src.providers.groq import GroqProvider
from src.config import ConfigManager


class ProviderFactory:
    @staticmethod
    def create(config: ConfigManager) -> AIProvider:
        provider_type = config.get("ai_provider", "openrouter")
        if provider_type == "openrouter":
            return OpenRouterProvider(
                config.get("openrouter_api_key", ""),
                config.get("openrouter_model", "openrouter/owl-alpha"),
            )
        if provider_type == "groq":
            return GroqProvider(
                config.get("groq_api_key", ""),
                config.get("groq_model", "llama3-70b-8192"),
            )
        raise ValueError(f"Unknown AI provider: {provider_type}")
