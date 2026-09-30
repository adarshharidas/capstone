# 30-Minute Capstone Demo Guide
 
This demo follows the required capstone presentation structure and uses
`INC-1042` as the main critical-path scenario.
 
## Presentation flow
 
| Section | Time | Demonstrate |
|---|---:|---|
| Problem statement | 3 min | Manual correlation between incidents, builds, deployments, alerts, and runbooks delays telecom operations response. |
| Architecture | 5 min | JSON inputs, LangGraph workflow, Gemini agents, FAISS runbooks, Streamlit dashboard, and Plotly charts. |
| Workflow explanation | 5 min | Intake, correlation, parallel analysis, router, RAG, recommendation, human approval, and report generation. |
| Live demo | 7 min | Analyze `INC-1042`, show critical routing, SLA risk, correlated failed build, retrieved runbook, approval, and report. |
| Challenges | 3 min | Synthetic data quality, grounding recommendations, graceful API fallback, and approval control. |
| Q&A | 7 min | Explain agent responsibilities, routing rules, RAG relevance, and reliability controls. |
 
## Failure scenarios to show
 
1. Run the critical incident before approval and show the `pending` state.
2. Reject the recommendation and show the rejected status in the report.
3. Analyze `INC-1044` to demonstrate a lower-severity staging workflow.
4. Run without `GEMINI_API_KEY` and explain the deterministic fallback used for local testing.
 
## Evidence to capture for evaluation
 
- Agent audit trail showing each workflow stage.
- Correlated build and deployment records.
- SLA status and escalation path.
- Retrieved runbook chunks and source names.
- Human approval decision.
- Stakeholder-ready Markdown report.
- Plotly dashboard metrics.
 