# TinyTroupe Persona Simulator — After-Tax Impact (Draft)

Run locally:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# create .env with OPENAI_API_KEY=...
streamlit run app/app.py

## Deliverable 2 — Beta Version & Technical Report

- **Run the beta app:** `streamlit run app/app.py`
- **How it works:** Select a persona, adjust assumptions, click **Simulate**. The app saves a transcript to `exports/` and example runs are checked into `deliverables/d2/examples/`.
- **Technical Report:** See `deliverables/d2/Deliverable-2_Technical_Report.md`.
- **Screenshots:** `deliverables/d2/screenshots/`.
