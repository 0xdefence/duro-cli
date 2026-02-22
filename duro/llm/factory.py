from __future__ import annotations
from .base import LLMProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .gemini_provider import GeminiProvider
from .anthropic_provider import AnthropicProvider
from .openrouter_provider import OpenRouterProvider


def get_provider(name: str, model: str = "") -> LLMProvider:
    n = (name or "").strip().lower()
    if n in ("", "mock"):
        return MockProvider()
    if n == "openai":
        return OpenAIProvider(model=model or "gpt-5")
    if n == "ollama":
        return OllamaProvider(model=model or "qwen2.5-coder:7b")
    if n in {"gemini", "google"}:
        return GeminiProvider(model=model or "gemini-2.5-pro")
    if n == "anthropic":
        return AnthropicProvider(model=model or "claude-sonnet-4-20250514")
    if n == "openrouter":
        return OpenRouterProvider(model=model or "openai/gpt-4.1-mini")

    # Stub for remaining provider
    if n in {"lmstudio"}:
        raise RuntimeError(f"Provider '{n}' not implemented yet; wire adapter in duro/llm/")

    raise RuntimeError(f"Unknown provider: {name}")
