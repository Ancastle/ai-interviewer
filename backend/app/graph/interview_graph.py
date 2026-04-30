from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.graph.state import InterviewState
from app.graph.nodes import (
    generate_question,
    wait_for_answer,
    evaluate_answer,
    generate_final_report,
    should_continue,
)

checkpointer = MemorySaver()


def build_graph():
    graph = StateGraph(InterviewState)

    graph.add_node("generate_question", generate_question)
    graph.add_node("wait_for_answer", wait_for_answer)
    graph.add_node("evaluate_answer", evaluate_answer)
    graph.add_node("generate_final_report", generate_final_report)

    graph.set_entry_point("generate_question")
    graph.add_edge("generate_question", "wait_for_answer")
    graph.add_edge("wait_for_answer", "evaluate_answer")
    graph.add_conditional_edges(
        "evaluate_answer",
        should_continue,
        {
            "continue": "generate_question",
            "wait": "wait_for_answer",
            "final_report": "generate_final_report",
        },
    )
    graph.add_edge("generate_final_report", END)

    return graph.compile(checkpointer=checkpointer, interrupt_before=["wait_for_answer"])


interview_graph = build_graph()
