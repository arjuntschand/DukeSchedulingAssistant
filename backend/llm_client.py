from __future__ import annotations

from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI


class LLMClient:
    """Thin wrapper around the OpenAI async client for chat and embeddings."""

    def __init__(
        self,
        api_key: str,
        chat_model: str,
        embedding_model: Optional[str] = None,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._chat_model = chat_model
        self._embedding_model = embedding_model

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        """Call the chat completion endpoint and return the assistant's reply text."""

        response = await self._client.chat.completions.create(
            model=self._chat_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
        )

        choice = response.choices[0]
        content = choice.message.content or ""
        if isinstance(content, list):
            # Newer models may return structured content; join text parts
            return "".join(part.get("text", "") for part in content if isinstance(part, dict))
        return str(content)

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts.

        If no embedding model is configured, return zero vectors of length 1 so the
        retriever can still function in a degraded, non-semantic mode.
        """

        if not self._embedding_model:
            return [[0.0] for _ in texts]

        response = await self._client.embeddings.create(
            model=self._embedding_model,
            input=texts,
        )

        return [item.embedding for item in response.data]
