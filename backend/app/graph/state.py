from typing import Annotated
from typing_extensions import TypedDict, NotRequired
from langgraph.graph.message import add_messages


class InterviewState(TypedDict):
    session_id: int
    model: str
    max_questions: int
    question_count: int
    current_question: str
    scores: list[dict]
    messages: Annotated[list, add_messages]
    langfuse_trace_id: str
    study_content: NotRequired[str]
