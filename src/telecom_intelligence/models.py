 
from __future__ import annotations
 
from typing import Any, Optional, TypedDict
 
 
class WorkflowState(TypedDict, total=False):
    incident: dict[str, Any]
    correlated_records: dict[str, Any]
    build_analysis: dict[str, Any]
    log_analysis: dict[str, Any]
    sla_analysis: dict[str, Any]
    routing: dict[str, Any]
    retrieved_context: list[dict[str, Any]]
    recommendation: dict[str, Any]
    approval_decision: Optional[str]
    approval_status: str
    report: dict[str, Any]
    audit_log: list[dict[str, Any]]
    error: Optional[str]
 
 
 
