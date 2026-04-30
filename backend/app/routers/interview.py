import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.openrouter import chat, chat_stream
from app.prompts.interviewer import build_interviewer_prompt
from app.prompts.evaluator import build_evaluator_prompt
from app.config import settings

router = APIRouter(prefix="/interview", tags=["interview"])


class StartRequest(BaseModel):
    cv: str
    job_description: str
    model: str = settings.default_model


class EvaluateRequest(BaseModel):
    question: str
    answer: str
    model: str = settings.default_model


@router.post("/start")
async def start_interview(req: StartRequest):
    system_prompt = build_interviewer_prompt(req.cv, req.job_description)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Start the interview."},
    ]
    async def stream():
        async for chunk in chat_stream(req.model, messages, trace_name="interview_start"):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/evaluate")
async def evaluate_answer(req: EvaluateRequest):
    messages = build_evaluator_prompt(req.question, req.answer)
    result = await chat(req.model, messages, trace_name="evaluate_answer")
    cleaned = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)
