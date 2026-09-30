 
import sys
from pathlib import Path
 
import streamlit as st
import plotly.express as px
 
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
 
from telecom_intelligence.config import get_settings
from telecom_intelligence.storage import load_dataset
from telecom_intelligence.workflow import run_incident, save_workflow_result
 
 
st.set_page_config(page_title="Telecom Operations Intelligence", layout="wide")
settings = get_settings()
datasets = load_dataset(settings.data_dir)
 
st.title("AI-Powered Telecom Operations, Build, and Incident Intelligence")
st.caption("Synthetic DevOps incident triage, SLA risk analysis, RAG guidance, and stakeholder reporting")
 
with st.sidebar:
    st.header("Incident analysis")
    options = {item["ticket_id"]: item["title"] for item in datasets["incidents"]}
    selected_id = st.selectbox("Select incident", list(options), format_func=lambda key: f"{key} - {options[key]}")
    analyze = st.button("Analyze incident", type="primary", use_container_width=True)
 
if analyze:
    st.session_state["workflow_state"] = run_incident(selected_id)
 
state = st.session_state.get("workflow_state")
if not state:
    st.info("Select an incident and click **Analyze incident** to run the multi-agent workflow.")
    st.stop()
 
summary = state["report"]["summary"]
sla = state["sla_analysis"]
route = state["routing"]
metrics = st.columns(5)
metrics[0].metric("Severity", summary["severity"])
metrics[1].metric("SLA", summary["sla_status"])
metrics[2].metric("Workflow", summary["workflow_path"])
metrics[3].metric("Approval", summary["approval_status"])
metrics[4].metric("RAG backend", "FAISS" if any("faiss" in e["message"] for e in state["audit_log"]) else "Fallback")
 
if state["approval_status"] == "pending":
    st.warning("Human approval is required before this critical recommendation can be treated as accepted.")
    approve, reject = st.columns(2)
    if approve.button("Approve recommendation", use_container_width=True):
        st.session_state["workflow_state"] = run_incident(selected_id, "approved")
        st.rerun()
    if reject.button("Reject recommendation", use_container_width=True):
        st.session_state["workflow_state"] = run_incident(selected_id, "rejected")
        st.rerun()
 
left, right = st.columns(2)
with left:
    st.subheader("Incident assessment")
    st.write(state["incident"].get("description", ""))
    st.json({"routing": route, "sla": sla, "recommendation": state["recommendation"]})
with right:
    st.subheader("Operational overview")
    status_counts = {}
    for item in datasets["builds"]:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
    figure = px.bar(x=list(status_counts), y=list(status_counts.values()), labels={"x": "Build status", "y": "Count"})
    st.plotly_chart(figure, use_container_width=True)
 
st.subheader("Retrieved runbook context")
for item in state.get("retrieved_context", []):
    with st.expander(f"{item['source']} (score: {item['score']})"):
        st.write(item["text"])
 
st.subheader("Stakeholder report")
st.markdown(state["report"]["markdown"])
if st.button("Save JSON result and Markdown report"):
    path = save_workflow_result(state, settings)
    st.success(f"Saved result to {path}")
 
with st.expander("Agent audit trail"):
    st.json(state.get("audit_log", []))
 
 
