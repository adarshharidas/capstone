 
from __future__ import annotations
 
from concurrent.futures import ThreadPoolExecutor
from typing import Any
 
from .config import Settings
from .llm import GeminiService
from .models import WorkflowState
from .rag import RunbookRetriever
from .reporting import build_report
from .tools import (
    analyze_alerts,
    analyze_builds,
    append_audit,
    calculate_sla,
    correlate_records,
)
 
 
def intake_node(state: WorkflowState, settings: Settings) -> WorkflowState:
    state = dict(state)
    incident = dict(state["incident"])
    incident["severity"] = incident.get("severity", "P3").upper()
    state["incident"] = incident
    append_audit(state, "intake_agent", "Normalized incident metadata.")
    return state
 
 
def correlation_node(state: WorkflowState, datasets: dict[str, Any]) -> WorkflowState:
    state = dict(state)
    state["correlated_records"] = correlate_records(
        state["incident"],
        datasets["builds"],
        datasets["deployments"],
        datasets["alerts"],
    )
    append_audit(state, "correlation_agent", "Linked incident to builds, deployments, and alerts.")
    return state
 
 
def parallel_analysis_node(state: WorkflowState, datasets: dict[str, Any]) -> WorkflowState:
    state = dict(state)
    records = state["correlated_records"]
    with ThreadPoolExecutor(max_workers=3) as executor:
        build_future = executor.submit(analyze_builds, records)
        log_future = executor.submit(analyze_alerts, records)
        sla_future = executor.submit(
            calculate_sla, state["incident"], datasets["sla_policies"]
        )
        state["build_analysis"] = build_future.result()
        state["log_analysis"] = log_future.result()
        state["sla_analysis"] = sla_future.result()
    append_audit(state, "parallel_analysis", "Completed build, alert, and SLA analysis concurrently.")
    return state
 
 
def route_node(state: WorkflowState) -> WorkflowState:
    state = dict(state)
    incident = state["incident"]
    critical = incident.get("severity") in {"P1", "P2"} or state["sla_analysis"].get(
        "status"
    ) in {"at_risk", "breached"}
    state["routing"] = {
        "path": "critical" if critical else "standard",
        "reason": "High severity or SLA risk" if critical else "Routine incident handling",
        "requires_approval": critical,
    }
    append_audit(state, "router_agent", f"Selected {state['routing']['path']} workflow path.")
    return state
 
 
def critical_review_node(state: WorkflowState) -> WorkflowState:
    state = dict(state)
    state["routing"]["escalation"] = "Network operations manager"
    append_audit(state, "critical_review_agent", "Prepared escalation review for a high-risk incident.")
    return state
 
 
def standard_review_node(state: WorkflowState) -> WorkflowState:
    state = dict(state)
    state["routing"]["escalation"] = "Service operations queue"
    append_audit(state, "standard_review_agent", "Prepared routine service-operations review.")
    return state
 
 
def rag_node(state: WorkflowState, retriever: RunbookRetriever) -> WorkflowState:
    state = dict(state)
    incident = state["incident"]
    query = " ".join(
        [
            incident.get("title", ""),
            incident.get("description", ""),
            " ".join(state.get("build_analysis", {}).get("signals", [])),
            " ".join(state.get("log_analysis", {}).get("signals", [])),
        ]
    )
    state["retrieved_context"] = retriever.retrieve(query)
    append_audit(state, "rag_agent", f"Retrieved runbook context using {retriever.backend}.")
    return state
 
 
def recommendation_node(state: WorkflowState, llm: GeminiService) -> WorkflowState:
    state = dict(state)
    incident = state["incident"]
    build_signals = state.get("build_analysis", {}).get("signals", [])
    log_signals = state.get("log_analysis", {}).get("signals", [])
    context = "\n".join(item["text"] for item in state.get("retrieved_context", []))
    fallback_action = (
        "Pause further rollout, compare the current release with the last healthy version, "
        "inspect the failed health checks, and escalate to the network operations manager."
        if state["routing"]["path"] == "critical"
        else "Assign the incident to service operations, inspect the correlated build and alert, "
        "and apply the matching runbook procedure."
    )
    prompt = f"""You are a telecom DevOps incident analyst.
Incident: {incident}
Build signals: {build_signals}
Alert signals: {log_signals}
Runbook context:
{context}
 
Return a concise recommended action and evidence for an operations stakeholder.
"""
    generated = None
    if llm.available:
        try:
            generated = llm.generate(prompt)
        except Exception as exc:  # fallback is intentionally graceful
            state["error"] = f"Gemini recommendation fallback: {exc}"
    state["recommendation"] = {
        "action": generated or fallback_action,
        "evidence": "; ".join(build_signals + log_signals)
        or "No correlated failure signals were found.",
        "model": "gemini" if generated else "deterministic-fallback",
    }
    append_audit(state, "recommendation_agent", "Generated an action recommendation.")
    return state
 
 
def approval_node(state: WorkflowState) -> WorkflowState:
    state = dict(state)
    if not state["routing"].get("requires_approval"):
        state["approval_status"] = "not_required"
    elif state.get("approval_decision") in {"approved", "rejected"}:
        state["approval_status"] = state["approval_decision"]
    else:
        state["approval_status"] = "pending"
    append_audit(state, "human_approval", f"Approval status: {state['approval_status']}.")
    return state
 
 
def report_node(state: WorkflowState) -> WorkflowState:
    state = dict(state)
    state["report"] = build_report(state)
    append_audit(state, "stakeholder_report_agent", "Created stakeholder-ready incident report.")
    return state
 
 
 