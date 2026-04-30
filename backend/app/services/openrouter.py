import json
import httpx
from typing import AsyncGenerator
from app.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {settings.openrouter_api_key}"}


async def chat(model: str, messages: list[dict]) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_URL,
            headers=HEADERS,
            json={"model": model, "messages": messages},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


async def chat_stream(model: str, messages: list[dict]) -> AsyncGenerator[str, None]:
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            OPENROUTER_URL,
            headers=HEADERS,
            json={"model": model, "messages": messages, "stream": True},
            timeout=30,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    yield content
