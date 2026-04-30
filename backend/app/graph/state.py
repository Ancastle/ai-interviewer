from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class InterviewState(TypedDict):
    session_id: int
    model: str
    max_questions: int
    question_count: int
    current_question: str
    scores: list[dict]
    messages: Annotated[list, add_messages]
    langfuse_trace_id: str
