from __future__ import annotations

from abc import ABC, abstractmethod

import google.generativeai as genai
import httpx

from .config import settings


class LlmAdapter(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiAdapter(LlmAdapter):
    def __init__(self) -> None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when MODEL_PROVIDER=gemini")
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    async def complete(self, prompt: str) -> str:
        response = await self.model.generate_content_async(prompt)
        return response.text


class OpenAICompatibleAdapter(LlmAdapter):
    def __init__(self, *, api_key: str | None, model: str, base_url: str, provider_name: str) -> None:
        if not api_key:
            raise ValueError(f"{provider_name.upper()}_API_KEY is required when MODEL_PROVIDER={provider_name}")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def complete(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload["choices"][0]["message"]["content"]


class AnthropicAdapter(LlmAdapter):
    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when MODEL_PROVIDER=anthropic")

    async def complete(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            payload = response.json()
            return "".join(block["text"] for block in payload["content"] if block["type"] == "text")


def build_llm() -> LlmAdapter:
    if settings.model_provider == "gemini":
        return GeminiAdapter()
    if settings.model_provider == "openai":
        return OpenAICompatibleAdapter(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            provider_name="openai",
        )
    if settings.model_provider == "groq":
        return OpenAICompatibleAdapter(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            base_url=settings.groq_base_url,
            provider_name="groq",
        )
    if settings.model_provider == "anthropic":
        return AnthropicAdapter()
    raise ValueError(f"Unsupported MODEL_PROVIDER: {settings.model_provider}")
