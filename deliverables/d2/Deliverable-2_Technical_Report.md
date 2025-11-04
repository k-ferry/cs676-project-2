# Deliverable 2 — Beta Version & Technical Report
**Project:** TinyTroupe Persona Simulator for Feature Feedback  
**Repo:** https://github.com/k-ferry/cs676-project-2  
**Date:** Oct 31, 2025

## 1) Objective
Deliver a beta app that simulates realistic persona feedback on product features, supports live conversation, and exports transcripts for analysis.

## 2) System Overview
- **UI:** Streamlit (`app/app.py`)
- **Agent runtime:** TinyTroupe `TinyPerson` (single-persona runs); personas in `app/personas.json`
- **Persistence:** Per-run Markdown + JSON to `exports/` (samples copied to `deliverables/d2/examples/`)
- **Config:** `.env` for `OPENAI_API_KEY`; optional `app/config.ini` for presets

## 3) Personas & Modeling
- **Validation & normalization.** Required: `name, biography, traits, constraints, device`. Recommended: `occupation, age, gender, location, education`. Missing recommended fields are defaulted (e.g., occupation=Product Manager).
- **Behavioral intent.** Traits/constraints steer tone and priorities (e.g., “impatient with extra clicks”; “one-hand use on mobile”).
- **Extensibility.** Add new entries to `app/personas.json`; the validator shields the UI from schema drift.

## 4) Conversation Flow (what changed in D2)
1. **Prompts**
   - **System:** Pins persona identity, enforces: *plain text*, *no meta words*, *first turn = 6 lines* (3 issues, 2 suggestions, 1 follow-up), callouts on a11y/speed/trust/copy/usability/discoverability.
   - **User:** Injects feature brief + an assumption summary from sliders.
2. **First turn (hardened)**
   - We send system + user via `tp.listen(...)`.
   - We **prime** with `tp.listen_and_act("Respond with a single TALK...")`.
   - We then call `tp.act(return_actions=True)` and extract text via a robust walker: `pick_text_from_actions(...)`.
   - Sanitization enforces the 3/2/1 line template and strips boilerplate echoes.
3. **Follow-up turns**
   - Strict prompt: “Add ONE new issue (tagged), ONE new suggestion, ONE concise question (all different from earlier).”
   - Same extract → sanitize pipeline, using the *followup* mode (1/1/1).
4. **Fallback safety**
   - If the agent returns nothing after retries, we insert a minimal, valid placeholder to keep runs usable and gradable.

## 5) Extraction & Cleaning (key D2 improvement)
- **Extractor (`pick_text_from_actions`).** Walks many payload shapes:
  - `{"action": {"type":"TALK","content":"..."}}`
  - `{"actions":[{"type":"TALK","content":"..."}]}`
  - OpenAI-like `{"choices":[{"message":{"content":"..."}}]}`
  - Nested `data/payload/result/output`, lists/tuples, and `.dict()`/`.model_dump()` objects.
- **Sanitizer (`_sanitize_reply`).**
  - Removes meta/echo lines, dedupes paragraphs, caps lines, and snaps to either **initial** (3/2/1) or **followup** (1/1/1) templates.

## 6) UI & Exports
- **Controls:** Persona dropdown; sliders for assumptions (mix, turnover, yield, etc.); scenario selector; turn count.
- **Outputs:** In-page transcript; quick manual ratings (clarity, confidence, likelihood); saved file paths.
- **Exports:** 
  - Markdown: readable transcript with scenario, assumptions, and ratings.
  - JSON: machine-friendly transcript plus full assumption payloads and persona metadata.

## 7) Design Choices & Trade-offs
- **TinyTroupe vs. raw LLM:** Agent layer is convenient, but we needed a custom extractor to handle varied action payloads.
- **Strict formatting vs. creativity:** We enforce a rubric for repeatability while allowing persona tone to come through.
- **Single-persona (D2) vs. multi-persona (D3):** Focus on stability andcriteria first.

## 8) Quality Controls
- **No-content mitigation:** Prime TALK, retry paths, final placeholder if needed.
- **Anti-repetition:** Prompt guardrails + sanitizer drops boilerplate (“Continue evaluating…”, “User experience considerations…”).
- **Persona schema diagnostics:** UI expander surfaces errors/warnings from `personas.json`.

## 9) Implementation Notes (files)
- `app/app.py` — Streamlit UI, persona validation, conversation loop, hardened extractor/sanitizer.
- `app/utils.py` — `load_personas`, `assumption_summary`, `save_markdown`, `ts`.
- `app/feature_presets.md` — Editable feature brief.
- `deliverables/d2/examples/` — Curated run outputs for grading.
- `deliverables/d2/screenshots/` — PNG screenshots of the UI.

## 10) Known Limitations
- Occasional restatement pressure from the model (mitigated; not eliminated).
- No persona-builder UI yet (JSON editing).
- No automated analytics (tag counts/charts) in-app yet.

## 11) Feedback → Changes (Round-2)
- **Empty turns** → Added TALK prime + multi-path extraction → resolved in testing.
- **Echoed boilerplate** → Sanitizer filters common LLM “meta commentary.”
- **Persona warnings** → Validator + defaults; UX expander surfaces schema health.

## 12) Roadmap (D3)
- Persona builder UI (with live validation).
- Analytics view (tag counts, turn trends, CSV export).
- Multi-persona comparisons; faster batching/caching.

## 13) How to Run
```bash
python -m venv .venv
. .venv/Scripts/activate     # Windows
pip install -r requirements.txt
# Put OPENAI_API_KEY in .env (see .env.example)
streamlit run app/app.py
