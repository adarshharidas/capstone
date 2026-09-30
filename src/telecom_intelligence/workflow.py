from __future__ import annotations
 
from pathlib import Path
from typing import Any
 
from .agents import (
    approval_node,
    correlation_node,
    critical_review_node,
    intake_node,
    parallel_analysis_node,
    rag_node,
    recommendation_node,
    report_node,
    route_node,
    standard_review_node,
)
from .config import Settings, get_settings
from .llm import GeminiService
from .models import WorkflowState
from .rag import RunbookRetriever
from .storage import load_dataset
 
try:
    from langgraph.graph import END, START, StateGraph
 
    LANGGRAPH_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised when dependencies are absent
    LANGGRAPH_AVAILABLE = False
 
 
def _route_selector(state: WorkflowState) -> str:
    return state.get("routing", {}).get("path", "standard")
 
 
def build_graph(
    datasets: dict[str, Any],
    settings: Settings,
    retriever: RunbookRetriever,
    llm: GeminiService,
):
    if not LANGGRAPH_AVAILABLE:
        return None
    graph = StateGraph(WorkflowState)
    graph.add_node("intake", lambda s: intake_node(s, settings))
    graph.add_node("correlation", lambda s: correlation_node(s, datasets))
    graph.add_node("parallel_analysis", lambda s: parallel_analysis_node(s, datasets))
    graph.add_node("route", route_node)
    graph.add_node("critical_review", critical_review_node)
    graph.add_node("standard_review", standard_review_node)
    graph.add_node("rag", lambda s: rag_node(s, retriever))
    graph.add_node("recommendation", lambda s: recommendation_node(s, llm))
    graph.add_node("approval", approval_node)
    graph.add_node("report", report_node)
    graph.add_edge(START, "intake")
    graph.add_edge("intake", "correlation")
    graph.add_edge("correlation", "parallel_analysis")
    graph.add_edge("parallel_analysis", "route")
    graph.add_conditional_edges(
        "route",
        _route_selector,
        {"critical": "critical_review", "standard": "standard_review"},
    )
    graph.add_edge("critical_review", "rag")
    graph.add_edge("standard_review", "rag")
    graph.add_edge("rag", "recommendation")
    graph.add_edge("recommendation", "approval")
    graph.add_edge("approval", "report")
    graph.add_edge("report", END)
    return graph.compile()
 
 
def run_incident(
    ticket_id: str,
    approval_decision: str | None = None,
    settings: Settings | None = None,
) -> WorkflowState:
    settings = settings or get_settings()
    datasets = load_dataset(settings.data_dir)
    incident = next(
        (item for item in datasets["incidents"] if item.get("ticket_id") == ticket_id),
        None,
    )
    if not incident:
        raise ValueError(f"Incident not found: {ticket_id}")
    retriever = RunbookRetriever(settings.documents_dir)
    llm = GeminiService(settings)
    initial: WorkflowState = {
        "incident": incident,
        "approval_decision": approval_decision,
        "audit_log": [],
    }
    graph = build_graph(datasets, settings, retriever, llm)
    if graph is not None:
        return graph.invoke(initial)
 
    state = intake_node(initial, settings)
    state = correlation_node(state, datasets)
    state = parallel_analysis_node(state, datasets)
    state = route_node(state)
    state = (
        critical_review_node(state)
        if state["routing"]["path"] == "critical"
        else standard_review_node(state)
    )
    state = rag_node(state, retriever)
    state = recommendation_node(state, llm)
    state = approval_node(state)
    return report_node(state)
 
 
def save_workflow_result(state: WorkflowState, settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    from .storage import save_json
 
    ticket_id = state["incident"]["ticket_id"]
    path = settings.outputs_dir / f"{ticket_id}.json"
    save_json(path, state)
    report_path = settings.outputs_dir / f"{ticket_id}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(state["report"]["markdown"], encoding="utf-8")
    return path