"""Registry for different LLM providers (OpenAI, Anthropic, etc.)."""

from typing import Callable, TypeVar
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

T = TypeVar("T", ChatOpenAI, ChatAnthropic)

ModelFactory = Callable[[str, bool], T]

MODEL_PROVIDERS: dict[str, ModelFactory] = {}


def register_provider(name: str, factory: ModelFactory) -> None:
    """Register a new model provider."""
    MODEL_PROVIDERS[name.lower()] = factory


def create_openai_model(model_name: str, streaming: bool) -> ChatOpenAI:
    """Create an OpenAI chat model instance."""
    return ChatOpenAI(model=model_name, streaming=streaming)


def create_anthropic_model(model_name: str, streaming: bool) -> ChatAnthropic:
    """Create an Anthropic chat model instance."""
    return ChatAnthropic(
        model_name=model_name,
        streaming=streaming,
        timeout=None,
        stop=None
    )


# Register available providers
register_provider("openai", create_openai_model)
register_provider("anthropic", create_anthropic_model)
