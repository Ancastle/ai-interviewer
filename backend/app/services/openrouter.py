import json
import httpx
from typing import AsyncGenerator
from app.config import settings
from app.services.langfuse import langfuse

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"
HEADERS = {"Authorization": f"Bearer {settings.openrouter_api_key}"}
EMBEDDING_MODEL = "openai/text-embedding-3-small"


async def chat(model: str, messages: list[dict], trace_name: str = "chat") -> str:
    trace = langfuse.trace(name=trace_name)
    generation = trace.generation(name="completion", model=model, input=messages)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_URL,
            headers=HEADERS,
            json={"model": model, "messages": messages},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    generation.end(
        output=content,
        usage={"input": usage.get("prompt_tokens"), "output": usage.get("completion_tokens")},
    )
    langfuse.flush()
    return content


async def chat_stream(model: str, messages: list[dict], trace_name: str = "chat_stream") -> AsyncGenerator[str, None]:
    trace = langfuse.trace(name=trace_name)
    generation = trace.generation(name="completion", model=model, input=messages)
    full_response = []

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
                    full_response.append(content)
                    yield content

    generation.end(output="".join(full_response))
    langfuse.flush()


async def embed(texts: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            EMBEDDINGS_URL,
            headers=HEADERS,
            json={"model": EMBEDDING_MODEL, "input": texts},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    return [item["embedding"] for item in data["data"]]
