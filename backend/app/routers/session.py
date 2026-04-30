import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select
from langgraph.types import Command
from app.graph.interview_graph import interview_graph
from app.services.langfuse import langfuse
from app.config import settings
from app.database import get_db
from app.models.message import Message
from app.models.session import Session as InterviewSession

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


@router.post("")
def create_session(db: DBSession = Depends(get_db)):
    session = InterviewSession(model=settings.default_model)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id}


class StudyStartRequest(BaseModel):
    session_id: int
    subject: str
    category_id: str
    model: str = settings.default_model
    max_questions: int = 5


@router.post("/study/start")
async def start_study_session(req: StudyStartRequest):
    from app.services.study_reader import get_study_guide
    study_content = get_study_guide(req.subject, req.category_id)

    config = {"configurable": {"thread_id": str(req.session_id)}}
    trace_id = str(uuid.uuid4())
    langfuse.trace(id=trace_id, name="study_session", metadata={"session_id": req.session_id, "subject": req.subject})

    initial_state = {
        "session_id": req.session_id,
        "model": req.model,
        "max_questions": req.max_questions,
        "question_count": 0,
        "current_question": "",
        "scores": [],
        "messages": [],
        "study_content": study_content,
        "langfuse_trace_id": trace_id,
    }
    state = await interview_graph.ainvoke(initial_state, config=config)
    graph_state = interview_graph.get_state(config)
    return _extract_response(state, graph_state)


@router.post("/start")
async def start_session(req: StartRequest):
    config = {"configurable": {"thread_id": str(req.session_id)}}
    trace_id = str(uuid.uuid4())
    langfuse.trace(id=trace_id, name="interview_session", metadata={"session_id": req.session_id})

    initial_state = {
        "session_id": req.session_id,
        "model": req.model,
        "max_questions": req.max_questions,
        "question_count": 0,
        "current_question": "",
        "scores": [],
        "messages": [],
        "langfuse_trace_id": trace_id,
    }
    state = await interview_graph.ainvoke(initial_state, config=config)
    graph_state = interview_graph.get_state(config)
    return _extract_response(state, graph_state)


@router.get("/{session_id}/history")
def get_history(session_id: int, db: DBSession = Depends(get_db)):
    messages = db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    ).scalars().all()
    return {
        "messages": [
            {"role": m.role.value, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in messages
        ]
    }


@router.post("/{session_id}/answer")
async def submit_answer(session_id: int, req: AnswerRequest):
    config = {"configurable": {"thread_id": str(session_id)}}
    state = await interview_graph.ainvoke(Command(resume=req.answer), config=config)
    graph_state = interview_graph.get_state(config)
    return _extract_response(state, graph_state)
