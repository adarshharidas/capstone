# Telecom Operations Intelligence

A Streamlit dashboard for analyzing synthetic telecom incidents using LangGraph, Gemini, and runbook retrieval. It correlates incidents with builds, deployments, alerts, and SLA policies, then produces recommendations and stakeholder reports with human approval.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Set `GEMINI_API_KEY` in `.env` to enable Gemini. The application includes a local fallback when Gemini is unavailable. Keep `.env` private.

Select an incident and click **Analyze incident**. Review the recommendation, approve or reject it when requested, and optionally save the JSON result and Markdown report to `outputs/`.

## Project layout

- `app.py`: Streamlit dashboard.
- `src/telecom_intelligence/`: workflow, agents, configuration, retrieval, and reporting.
- `src/telecom_intelligence/data/`: synthetic input datasets.
- `src/telecom_intelligence/documents/runbooks/`: reference runbooks.
- `src/telecom_intelligence/docs/demo-guide.md`: presentation guide.

Virtual environments, secrets, caches, and generated outputs are excluded from Git.
