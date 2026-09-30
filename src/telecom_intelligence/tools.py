 
from __future__ import annotations
 
from datetime import datetime, timezone
from typing import Any
 
 
def correlate_records(
    incident: dict[str, Any],
    builds: list[dict[str, Any]],
    deployments: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Correlate operational records using stable IDs plus service matching."""
    pipeline_id = incident.get("pipeline_id")
    release_version = incident.get("release_version")
    service = incident.get("service")
    related_builds = [
        item
        for item in builds
        if item.get("pipeline_id") == pipeline_id
        or item.get("release_version") == release_version
        or item.get("service") == service
    ]
    related_deployments = [
        item
        for item in deployments
        if item.get("release_version") == release_version
        or item.get("service") == service
    ]
    related_alerts = [
        item
        for item in alerts
        if item.get("incident_id") == incident.get("ticket_id")
        or item.get("service") == service
    ]
    return {
        "builds": related_builds,
        "deployments": related_deployments,
        "alerts": related_alerts,
    }
 
 
def analyze_builds(records: dict[str, Any]) -> dict[str, Any]:
    builds = records.get("builds", [])
    deployments = records.get("deployments", [])
    failed_builds = [b for b in builds if b.get("status") == "failed"]
    failed_deployments = [
        d
        for d in deployments
        if d.get("status") in {"failed", "rolled_back"}
        or d.get("health_check") == "failed"
    ]
    return {
        "build_count": len(builds),
        "failed_build_count": len(failed_builds),
        "failed_builds": failed_builds,
        "deployment_count": len(deployments),
        "failed_deployment_count": len(failed_deployments),
        "failed_deployments": failed_deployments,
        "signals": [
            b.get("failure_reason")
            for b in failed_builds
            if b.get("failure_reason")
        ]
        + [
            d.get("health_message")
            for d in failed_deployments
            if d.get("health_message")
        ],
    }
 
 
def analyze_alerts(records: dict[str, Any]) -> dict[str, Any]:
    alerts = records.get("alerts", [])
    active = [a for a in alerts if a.get("status") == "active"]
    return {
        "alert_count": len(alerts),
        "active_alert_count": len(active),
        "active_alerts": active,
        "signals": [a.get("message", "") for a in active],
    }
 
 
def calculate_sla(
    incident: dict[str, Any],
    policies: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Calculate response/resolution risk from the incident's priority policy."""
    priority = incident.get("severity", "P3").upper()
    policy = policies.get(priority, policies.get("P3", {}))
    created_at = datetime.fromisoformat(incident["created_at"])
    now = now or datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    elapsed_minutes = max(0, int((now - created_at).total_seconds() / 60))
    response_limit = int(policy.get("response_minutes", 60))
    resolution_limit = int(policy.get("resolution_minutes", 480))
    acknowledged = bool(incident.get("acknowledged", False))
    response_risk = not acknowledged and elapsed_minutes >= response_limit
    resolution_risk = elapsed_minutes >= resolution_limit
    status = "breached" if resolution_risk else "at_risk" if response_risk else "within_sla"
    return {
        "priority": priority,
        "status": status,
        "elapsed_minutes": elapsed_minutes,
        "response_limit_minutes": response_limit,
        "resolution_limit_minutes": resolution_limit,
        "response_risk": response_risk,
        "resolution_risk": resolution_risk,
        "recommended_action": (
            "Escalate immediately"
            if status in {"breached", "at_risk"}
            else "Continue standard response"
        ),
    }
 
 
def append_audit(state: dict[str, Any], agent: str, message: str) -> None:
    state.setdefault("audit_log", []).append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "message": message,
        }
    )
 
 
 