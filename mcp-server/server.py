import os
import httpx
from mcp.server.fastmcp import FastMCP

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

mcp = FastMCP("interview-coach")


@mcp.tool()
async def search_resume(session_id: int, query: str, top_k: int = 3) -> list[str]:
    """Search the candidate's CV/resume for chunks relevant to the query."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BACKEND_URL}/documents/search",
            json={"session_id": session_id, "doc_type": "cv", "query": query, "top_k": top_k},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["results"]


@mcp.tool()
async def search_jd(session_id: int, query: str, top_k: int = 3) -> list[str]:
    """Search the job description for chunks relevant to the query."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BACKEND_URL}/documents/search",
            json={"session_id": session_id, "doc_type": "job_description", "query": query, "top_k": top_k},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["results"]


@mcp.tool()
async def get_session_history(session_id: int) -> list[dict]:
    """Return the full message history (role + content) for an interview session."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BACKEND_URL}/session/{session_id}/history",
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["messages"]


if __name__ == "__main__":
    mcp.run()
