import json
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import interrupt
from app.graph.state import InterviewState
from app.services.openrouter import chat, embed
from app.services.vector_store import search
from app.services.langfuse import langfuse
from app.prompts.interviewer import build_interviewer_prompt
from app.prompts.study_interviewer import build_study_interviewer_prompt
from app.prompts.evaluator import build_evaluator_prompt


def _get_span(state: InterviewState, name: str):
    trace = langfuse.trace(id=state["langfuse_trace_id"], name="interview_session")
    return trace.span(name=name)


async def generate_question(state: InterviewState) -> dict:
    span = _get_span(state, "generate_question")
    study_content = state.get("study_content", "")

    if study_content:
        system_prompt = build_study_interviewer_prompt(study_content)
    else:
        query = state["current_question"] or "technical skills and experience"
        cv_chunks = search(state["session_id"], "cv", (await embed([query]))[0])
        jd_chunks = search(state["session_id"], "job_description", (await embed([query]))[0])
        system_prompt = build_interviewer_prompt("\n\n".join(cv_chunks), "\n\n".join(jd_chunks))
    messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m.type, "content": m.content}
        for m in state["messages"]
    ]

    question = await chat(state["model"], messages, trace_name="generate_question", parent=span)

    span.end()

    return {
        "messages": [AIMessage(content=question)],
        "current_question": question,
        "question_count": state["question_count"] + 1,
    }


async def wait_for_answer(state: InterviewState) -> dict:
    answer = interrupt("Waiting for user answer")
    return {"messages": [HumanMessage(content=answer)]}


async def evaluate_answer(state: InterviewState) -> dict:
    question = state["current_question"]
    answer = state["messages"][-1].content

    if len(answer.strip()) < 20:
        follow_up = AIMessage(content="Could you elaborate a bit more on that?")
        return {"messages": [follow_up]}

    span = _get_span(state, "evaluate_answer")
    messages = build_evaluator_prompt(question, answer)
    result = await chat(state["model"], messages, trace_name="evaluate_answer", parent=span)
    span.end()

    cleaned = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    evaluation = json.loads(cleaned)

    return {"scores": state["scores"] + [evaluation]}


async def generate_final_report(state: InterviewState) -> dict:
    scores = state["scores"]
    if not scores:
        return {"messages": [AIMessage(content="No answers were evaluated.")]}

    avg = lambda key: sum(s["scores"][key] for s in scores) / len(scores)
    summary = {
        "accuracy": avg("accuracy"),
        "depth": avg("depth"),
        "clarity": avg("clarity"),
        "relevance": avg("relevance"),
        "overall": sum(s["overall"] for s in scores) / len(scores),
    }

    report_prompt = f"""You are an interview coach. Based on these evaluation scores, write a concise final report for the candidate.

Scores (1-5):
- Accuracy: {summary['accuracy']:.1f}
- Depth: {summary['depth']:.1f}
- Clarity: {summary['clarity']:.1f}
- Relevance: {summary['relevance']:.1f}
- Overall: {summary['overall']:.1f}

Individual feedback:
{chr(10).join(f"Q{i+1}: {s['feedback']}" for i, s in enumerate(scores))}

Write a 3-4 sentence summary: what went well, what to improve, and an honest overall assessment."""

    span = _get_span(state, "generate_final_report")
    report = await chat(
        state["model"],
        [{"role": "user", "content": report_prompt}],
        trace_name="final_report",
        parent=span,
    )
    span.end()
    return {"messages": [AIMessage(content=report)]}


def should_continue(state: InterviewState) -> str:
    if state["question_count"] >= state["max_questions"]:
        return "final_report"
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and "elaborate" in last_message.content.lower():
        return "wait"
    return "continue"
