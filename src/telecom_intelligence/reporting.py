 
from __future__ import annotations
 
from typing import Any
 
 
def build_report(state: dict[str, Any]) -> dict[str, Any]:
    incident = state["incident"]
    sla = state.get("sla_analysis", {})
    route = state.get("routing", {})
    recommendation = state.get("recommendation", {})
    report = (
        f"# Incident Report: {incident.get('ticket_id')}\n\n"
        f"**Summary:** {incident.get('title')}\n\n"
        f"- Service: {incident.get('service')}\n"
        f"- Environment: {incident.get('environment')}\n"
        f"- Severity: {incident.get('severity')}\n"
        f"- Release: {incident.get('release_version')}\n"
        f"- Workflow path: {route.get('path', 'standard')}\n"
        f"- SLA status: {sla.get('status', 'unknown')}\n"
        f"- Approval status: {state.get('approval_status', 'not_required')}\n\n"
        f"## Recommendation\n\n{recommendation.get('action', 'No recommendation generated.')}\n\n"
        f"## Evidence\n\n{recommendation.get('evidence', 'No evidence recorded.')}\n"
    )
    return {
        "markdown": report,
        "summary": {
            "ticket_id": incident.get("ticket_id"),
            "severity": incident.get("severity"),
            "sla_status": sla.get("status"),
            "workflow_path": route.get("path"),
            "approval_status": state.get("approval_status"),
        },
    }
 
 
 