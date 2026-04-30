from fastapi import APIRouter
from pydantic import BaseModel
from langgraph.types import Command
from app.graph.interview_graph import interview_graph
from app.config import settings

router = APIRouter(prefix="/session", tags=["session"])


class StartRequest(BaseModel):
    session_id: int
    model: str = settings.default_model
    max_questions: int = 5


class AnswerRequest(BaseModel):
    answer: str


def _extract_response(state: dict, graph_state) -> dict:
    last_message = state["messages"][-1]
    is_done = not graph_state.next

    if is_done:
        return {"done": True, "report": last_message.content, "scores": state["scores"]}
    return {"done": False, "question": last_message.content}


@router.post("/start")
async def start_session(req: StartRequest):
    config = {"configurable": {"thread_id": str(req.session_id)}}
    initial_state = {
        "session_id": req.session_id,
        "model": req.model,
        "max_questions": req.max_questions,
        "question_count": 0,
        "current_question": "",
        "scores": [],
        "messages": [],
    }
    state = await interview_graph.ainvoke(initial_state, config=config)
    graph_state = interview_graph.get_state(config)
    return _extract_response(state, graph_state)


@router.post("/{session_id}/answer")
async def submit_answer(session_id: int, req: AnswerRequest):
    config = {"configurable": {"thread_id": str(session_id)}}
    state = await interview_graph.ainvoke(Command(resume=req.answer), config=config)
    graph_state = interview_graph.get_state(config)
    return _extract_response(state, graph_state)
