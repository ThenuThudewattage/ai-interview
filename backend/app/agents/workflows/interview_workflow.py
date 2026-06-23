"""LangGraph interview workflow — compiled state machine."""
import logging

from langgraph.graph import END, StateGraph

from app.agents.workflows.nodes import (
    analyze_and_adjust_node,
    conclude_node,
    evaluate_answer_node,
    generate_question_node,
    initialize_node,
    learning_analysis_node,
    orchestrator_router,
    process_answer_node,
)
from app.agents.workflows.states import InterviewState

logger = logging.getLogger(__name__)

_compiled_graph = None


def create_interview_workflow():
    """Create and compile the LangGraph interview workflow."""
    workflow = StateGraph(InterviewState)

    # ── Add nodes ─────────────────────────────────────────────
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("generate_question", generate_question_node)
    workflow.add_node("process_answer", process_answer_node)
    workflow.add_node("evaluate_answer", evaluate_answer_node)
    workflow.add_node("analyze_and_adjust", analyze_and_adjust_node)
    workflow.add_node("learning_analysis", learning_analysis_node)
    workflow.add_node("conclude_interview", conclude_node)

    # ── Set entry point ────────────────────────────────────────
    workflow.set_entry_point("initialize")

    # ── Add edges ─────────────────────────────────────────────
    workflow.add_edge("initialize", "generate_question")
    workflow.add_edge("generate_question", "process_answer")  # Wait for answer input
    workflow.add_edge("process_answer", "evaluate_answer")
    workflow.add_edge("evaluate_answer", "learning_analysis")
    workflow.add_edge("learning_analysis", "analyze_and_adjust")

    # Conditional: after analyze, either ask next question or conclude
    workflow.add_conditional_edges(
        "analyze_and_adjust",
        orchestrator_router,
        {
            "generate_question": "generate_question",
            "conclude_interview": "conclude_interview",
        },
    )

    workflow.add_edge("conclude_interview", END)

    return workflow.compile()


def get_compiled_workflow():
    """Get or create the compiled workflow (singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = create_interview_workflow()
        logger.info("✅ LangGraph interview workflow compiled")
    return _compiled_graph
