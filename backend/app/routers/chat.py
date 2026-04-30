import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.openrouter import chat, chat_stream

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    model: str
    messages: list[dict]


@router.post("")
async def post_chat(req: ChatRequest):
    content = await chat(req.model, req.messages)
    return {"content": content}


@router.post("/stream")
async def post_chat_stream(req: ChatRequest):
    async def event_generator():
        async for chunk in chat_stream(req.model, req.messages):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
