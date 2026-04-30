from fastapi import APIRouter
from pydantic import BaseModel
from app.services.openrouter import chat

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    model: str
    messages: list[dict]


@router.post("")
async def post_chat(req: ChatRequest):
    content = await chat(req.model, req.messages)
    return {"content": content}
