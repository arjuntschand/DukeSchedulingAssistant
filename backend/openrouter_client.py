from __future__ import annotations

from typing import List, Dict, Any

import httpx

from .config import get_settings


# Base OpenRouter API URL; specific endpoints are appended to this.
API_URL = "https://openrouter.ai/api/v1"


class OpenRouterClient:
    """Thin async client for OpenRouter chat completions.

    This client takes OpenAI-style message lists and returns the
    assistant's content string.
    """

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")

        self._api_key = settings.openrouter_api_key
        self._model = settings.openrouter_model

    async def chat(self, messages: List[Dict[str, Any]], temperature: float = 0.2) -> str:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            # Optional but recommended by OpenRouter docs
            "HTTP-Referer": "http://localhost:5173/",
            "X-Title": "Duke Pratt Degree Planning Assistant",
        }

        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{API_URL}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        return data["choices"][0]["message"]["content"]
