# app/app.py
import os
import textwrap
import warnings
import streamlit as st
from dotenv import load_dotenv

# Keep this import only — it's stable across TinyTroupe versions
from tinytroupe.agent import TinyPerson
import tinytroupe.control as control

from utils import load_personas, assumption_summary, save_markdown, ts
from after_tax_regression import run_after_tax_regression

# Quiet a noisy pydantic warning some users see
warnings.filterwarnings("ignore", message=".*UnsupportedFieldAttributeWarning.*")

# Helpers
import re, json
from typing import List, Dict, Any

def _safe_read(path: str, fallback: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return fallback

@st.cache_data
def _load_personas_cached(path: str) -> List[Dict[str, Any]]:
    return load_personas(path)

def _init_chat():
    if "chat" not in st.session_state:
        st.session_state.chat = []  # [{"role": "user"|"assistant", "name": str|None, "content": str}]

def _push(role: str, content: str, name: str | None = None):
    st.session_state.chat.append({"role": role, "name": name, "content": content})

def _render_chat():
    for m in st.session_state.chat:
        label = m["name"] if (m["name"] and m["role"] == "assistant") else ("You" if m["role"] == "user" else "System")
        with st.chat_message("assistant" if m["role"]=="assistant" else "user"):
            st.markdown(f"**{label}:** {m['content']}")

_TAG_RE = re.compile(r"\b(usability|copy|trust|speed|a11y|discoverability)\b", flags=re.IGNORECASE)

def count_tags(text: str) -> Dict[str, int]:
    counts = {k: 0 for k in ["usability", "copy", "trust", "speed", "a11y", "discoverability"]}
    for m in _TAG_RE.findall(text or ""):
        counts[m.lower()] += 1
    return counts

def merge_counts(a: Dict[str, int], b: Dict[str, int]) -> Dict[str, int]:
    return {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}

import re

_META_PAT = re.compile(r'\b(TALK|DONE)\b', re.IGNORECASE)
_ECHO_PAT = re.compile(r'^Evaluate the feature.*$', re.IGNORECASE)

def _strip_meta(text: str) -> str:
    if not text:
        return text
    DROP_PREFIXES = (
        "TALK", "DONE", "Evaluate the feature and assumptions",
        "Feature evaluation for", "Assumptions regarding", "I feel a sense of urgency",
        "Continue evaluating", "User experience considerations", "Focusing on ",
        "Impatient with ", "Frustrated with ", "The feature's complexity and the need",
    )
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s:
            continue
        if any(s.startswith(p) for p in DROP_PREFIXES):
            continue
        # drop headings-y stuff
        if s.lower().startswith(("feature evaluation", "assumptions", "outputs:")):
            continue
        lines.append(s)
    return "\n".join(lines)


def _dedupe_paragraphs(text: str) -> str:
    if not text:
        return text
    parts = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    out, seen = [], set()
    for p in parts:
        if p not in seen:
            out.append(p); seen.add(p)
    return "\n\n".join(out)

def _trim_lines(text: str, max_lines: int) -> str:
    if not text:
        return text
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines[:max_lines])

def _enforce_template_initial(text: str) -> str:
    """
    Keep exactly: 3 issue lines, 2 suggestion lines, 1 question line (in that order).
    We detect by simple keywords; if missing, we take first non-empty lines.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    issues, suggs, qs = [], [], []
    for ln in lines:
        low = ln.lower()
        if len(issues) < 3 and ("issue" in low or any(t in low for t in ["usability","copy","trust","speed","a11y","discoverability"])):
            issues.append(ln); continue
        if len(suggs) < 2 and ("suggestion" in low or low.startswith(("try ", "consider ", "add ", "implement "))):
            suggs.append(ln); continue
        if not qs and ("?" in ln or low.startswith("follow-up") or low.startswith("question")):
            qs = [ln]; continue
    # fallback fills from remaining lines in order
    rest = [ln for ln in lines if ln not in issues + suggs + qs]
    while len(issues) < 3 and rest: issues.append(rest.pop(0))
    while len(suggs) < 2 and rest: suggs.append(rest.pop(0))
    if not qs and rest: qs = [rest.pop(0)]
    ordered = issues + suggs + qs
    return "\n".join(ordered[:6])

def _enforce_template_followup(text: str) -> str:
    """
    Keep exactly: 1 issue, 1 suggestion, 1 question (3 lines).
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    issue = next((ln for ln in lines if ("issue" in ln.lower() or any(t in ln.lower() for t in ["usability","copy","trust","speed","a11y","discoverability"]))), None)
    suggestion = next((ln for ln in lines if ("suggestion" in ln.lower() or ln.lower().startswith(("try ","consider ","add ","implement ")))), None)
    question = next((ln for ln in lines if "?" in ln or ln.lower().startswith(("follow-up","question"))), None)
    ordered = [x for x in [issue, suggestion, question] if x]
    # Fallbacks if any are missing
    rest = [ln for ln in lines if ln not in ordered]
    while len(ordered) < 3 and rest:
        ordered.append(rest.pop(0))
    return "\n".join(ordered[:3])

def _sanitize_reply(text: str, mode: str, prev_text: str | None = None) -> str:
    # 1) strip meta/echo
    text = _strip_meta(text)
    # 2) collapse duplicated paragraphs
    text = _dedupe_paragraphs(text)
    # 3) drop exact previous reply
    if prev_text and text.strip() == prev_text.strip():
        text = text.splitlines()[0]
    # 4) enforce template + line cap
    if mode == "initial":
        text = _enforce_template_initial(text)
        text = _trim_lines(text, 6)
    else:
        text = _enforce_template_followup(text)
        text = _trim_lines(text, 3)
    return text.strip()


# ===== Persona validation / normalization =====
RECOMMENDED_FIELDS = ["occupation", "age", "gender", "location", "education"]

def validate_persona(p: dict) -> dict:
    """Return {'errors': [...], 'warnings': [...], 'normalized': dict}."""
    errors, warnings = [], []
    norm = dict(p)  # shallow copy

    # Required
    for k in ["name", "biography", "traits", "constraints", "device"]:
        if k not in p:
            errors.append(f"Missing required field: {k}")

    # Types
    if "traits" in p and not isinstance(p["traits"], list):
        errors.append("traits must be a list of strings")
    if "constraints" in p and not isinstance(p["constraints"], list):
        errors.append("constraints must be a list of strings")

    # Recommendations
    for k in RECOMMENDED_FIELDS:
        if k not in p:
            warnings.append(f"Recommended field missing: {k}")

    # Normalizations
    norm.setdefault("occupation", "Product Manager")
    norm.setdefault("age", 35)
    norm.setdefault("gender", "unspecified")
    norm.setdefault("location", "USA")
    norm.setdefault("education", "Bachelor's")

    # Ensure lists are clean
    if isinstance(norm.get("traits"), list):
        norm["traits"] = [str(t).strip() for t in norm["traits"] if str(t).strip()]
    if isinstance(norm.get("constraints"), list):
        norm["constraints"] = [str(c).strip() for c in norm["constraints"] if str(c).strip()]

    return {"errors": errors, "warnings": warnings, "normalized": norm}

def safe_tt_turn(tp, *, prefer_actions=True, force_talk=False):
    try:
        if force_talk:
            return tp.listen_and_act(
                "Respond now with a single TALK action whose content is plain text (no JSON)."
            )
        if prefer_actions:
            return tp.act(return_actions=True)
        return tp.act()
    except Exception as e:
        return {"error": repr(e)}

# 1) Load env + page setup
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="TinyTroupe Persona Simulator", layout="wide")
st.title("TinyTroupe Persona Simulator — After-Tax Impact (Draft)")

_init_chat()

if not OPENAI_KEY:
    st.warning("OPENAI_API_KEY not found. Create a .env in the project root and restart the app.")
    st.stop()

# 2) UI layout
col1, col2 = st.columns([1, 2])

with col1:
    # Personas + schema health
    raw_personas = _load_personas_cached("app/personas.json")
    validated = [validate_persona(p) for p in raw_personas]
    err_ct = sum(len(v["errors"]) for v in validated)
    warn_ct = sum(len(v["warnings"]) for v in validated)
    if err_ct:
        st.error(f"Persona file: {err_ct} errors, {warn_ct} warnings")
    elif warn_ct:
        st.warning(f"Persona file: {warn_ct} warnings (no errors)")
    else:
        st.caption("Persona file: ✅ schema OK")
    with st.expander("Persona schema diagnostics", expanded=False):
        for i, v in enumerate(validated):
            name = raw_personas[i].get("name", f"Persona {i+1}")
            if v["errors"]:
                st.write(f"❌ **{name}** errors: {v['errors']}")
            if v["warnings"]:
                st.write(f"⚠️ **{name}** warnings: {v['warnings']}")

    personas = [v["normalized"] for v in validated]
    persona_names = [p["name"] for p in personas]
    persona = st.selectbox("Persona", persona_names)

    # Assumptions (these drive your scenario)
    st.subheader("Assumptions")
    us_eq   = st.slider("US Equity %", 0, 100, 40)
    intl_eq = st.slider("Intl Equity %", 0, 100, 20)
    fi      = st.slider("Fixed Income %", 0, 100, 15)
    altshf  = st.slider("Alts HF %", 0, 100, 5)
    altspe  = st.slider("Alts PE %", 0, 100, 10)
    altsre  = st.slider("Alts RE %", 0, 100, 5)
    cash    = st.slider("Cash %", 0, 100, 5)

    turnover = st.slider("Turnover %", 0, 100, 40)
    yield_   = st.slider("Yield %", 0, 20, 2)

    horizon  = st.select_slider("Horizon (years)", options=[1, 3, 5], value=1)
    lots     = st.selectbox("Lot Selection", ["FIFO", "Specific ID"])
    harvest  = st.selectbox("Harvest Losses", ["ON", "OFF"])
    reinvest = st.selectbox("Reinvest Distributions", ["Yes", "No"])

    ord_rate  = st.slider("Ordinary Tax Rate %", 0, 55, 37)
    ltcg_rate = st.slider("LTCG Rate %", 0, 35, 20)
    niit      = st.slider("NIIT %", 0, 5, 3)
    state_rt  = st.slider("State Tax %", 0, 15, 6)

    tax_deferred = st.slider("Tax-Deferred %", 0, 100, 20)
    tax_exempt   = st.slider("Tax-Exempt %", 0, 100, 0)

    # Feature brief
    feature_spec = st.text_area(
        "Feature Brief (edit as needed)",
        height=220,
        value=_safe_read(
            "app/feature_presets.md",
            "Feature: After-Tax Impact module. Show tax drag, harvest toggles, lot selection, reinvest on/off, turnover, yield."
        ),
    )

    scenario = st.selectbox(
        "Scenario",
        [
            "First look (discovery + immediate reaction)",
            "Guided task (compare Harvest ON vs OFF)",
            "Week-later (annoyances & delighters)",
        ],
    )
    turns = st.slider("Conversation turns", 1, 8, 4)

# Build assumptions dict + summary
assumptions = {
    "us_eq": us_eq,
    "intl_eq": intl_eq,
    "fi": fi,
    "altshf": altshf,
    "altspe": altspe,
    "altsre": altsre,
    "cash": cash,
    "turnover": turnover,
    "yield": yield_,
    "horizon": horizon,
    "lots": lots,
    "harvest": harvest,
    "reinvest": reinvest,
    "ord_rate": ord_rate,
    "ltcg_rate": ltcg_rate,
    "niit": niit,
    "state_rate": state_rt,
    "tax_deferred": tax_deferred,
    "tax_exempt": tax_exempt,
}
assumption_text = assumption_summary(assumptions)

import hashlib

def _clean_reply(raw: str, seen_hashes: set[str]) -> str:
    if not isinstance(raw, str):
        return ""

    # Drop boilerplate lines and obvious meta noise
    drop_prefixes = ("TALK", "DONE", "Evaluate the feature and assumptions", 
                     "Feature evaluation for", "Assumptions regarding", 
                     "I feel a sense of urgency")
    lines = []
    for ln in raw.splitlines():
        s = ln.strip()
        if not s:
            continue
        if any(s.startswith(p) for p in drop_prefixes):
            continue
        lines.append(s)

    # Chunk by blank lines and dedupe semantically similar paragraphs
    cleaned = []
    buf = []
    def flush():
        if not buf:
            return
        paragraph = " ".join(buf).strip()
        h = hashlib.md5(paragraph.lower().encode("utf-8")).hexdigest()
        if h not in seen_hashes:
            seen_hashes.add(h)
            cleaned.append(paragraph)
        buf.clear()

    for s in lines:
        if s == "":
            flush()
        else:
            buf.append(s)
    flush()

    return "\n\n".join(cleaned).strip()

def pick_text_from_actions(payload) -> str:
    """
    Extract plain text from a wide variety of TinyTroupe / LLM reply shapes.
    Handles:
    - {"action": {"type":"TALK","content":"..."}}
    - {"actions": [ {"type":"TALK","content":"..."}, ... ]}
    - {"type":"TALK","content":"..."}  (top-level)
    - {"content": "..."} / {"text":"..."} / {"message":"..."}
    - OpenAI-like {"choices":[{"message":{"content":"..."}}]}
    - {"data": ...} / {"payload": ...} / {"result": ...} / {"output": ...}
    - lists/tuples of any of the above
    - arbitrary objects with .dict() / .model_dump() / __dict__
    Returns a single newline-joined string.
    """
    texts = []

    def maybe_add(s):
        if isinstance(s, str):
            s = s.strip()
            if s:
                texts.append(s)

    def visit(obj):
        if obj is None:
            return

        # String
        if isinstance(obj, str):
            maybe_add(obj)
            return

        # List/Tuple
        if isinstance(obj, (list, tuple)):
            for item in obj:
                visit(item)
            return

        # Dict-like
        if isinstance(obj, dict):
            # OpenAI-like choices/message
            ch = obj.get("choices")
            if isinstance(ch, list) and ch:
                for choice in ch:
                    if isinstance(choice, dict):
                        msg = choice.get("message")
                        if isinstance(msg, dict):
                            maybe_add(msg.get("content"))
                # still traverse for any extra text
                for choice in ch:
                    visit(choice)

            # common content keys
            for k in ("content", "text", "message"):
                maybe_add(obj.get(k))

            # singular action
            if "action" in obj:
                a = obj["action"]
                if isinstance(a, dict):
                    t = str(a.get("type", "")).upper()
                    c = a.get("content") or a.get("text") or a.get("message")
                    if t in {"TALK", "SAY", "SPEAK", "REPLY"}:
                        maybe_add(c)
                else:
                    t = str(a).upper()
                    if t in {"TALK", "SAY", "SPEAK", "REPLY"}:
                        c = obj.get("content") or obj.get("text") or obj.get("message")
                        maybe_add(c)

            # plural actions
            if "actions" in obj and isinstance(obj["actions"], list):
                for a in obj["actions"]:
                    if isinstance(a, dict):
                        t = str(a.get("type", "")).upper()
                        if t in {"TALK", "SAY", "SPEAK", "REPLY"}:
                            c = a.get("content") or a.get("text") or a.get("message")
                            maybe_add(c)
                    visit(a)

            # top-level type/content
            if "type" in obj:
                t = str(obj.get("type", "")).upper()
                if t in {"TALK", "SAY", "SPEAK", "REPLY"}:
                    c = obj.get("content") or obj.get("text") or obj.get("message")
                    maybe_add(c)

            # nested containers
            for k in ("data", "payload", "result", "output"):
                if k in obj:
                    visit(obj[k])

            # catch-all dive
            for v in obj.values():
                visit(v)
            return

        # model_dump/dict/__dict__
        for attr in ("model_dump", "dict"):
            if hasattr(obj, attr) and callable(getattr(obj, attr)):
                try:
                    visit(getattr(obj, attr)())
                    return
                except Exception:
                    pass

        d = getattr(obj, "__dict__", None)
        if isinstance(d, dict):
            try:
                visit({k: v for k, v in d.items() if not str(k).startswith("_")})
                return
            except Exception:
                pass

    visit(payload)
    # join unique non-empty lines to reduce accidental duplicates
    out = "\n".join([t for t in texts if t])
    return out.strip()



with col2:
    st.subheader("Run Simulation")

    if st.button("Simulate"):
        # 1) Get the chosen persona
        P = [p for p in personas if p["name"] == persona][0]

        # 2) Build the TinyPerson (unchanged from your version) …
        agent_spec = {
            "type": "TinyPerson",
            "persona": {
                "name": P.get("name", "Unnamed Persona"),
                "biography": P.get("biography", "No biography provided."),
                "personality": {"traits": P.get("traits", ["practical", "direct"])},
                "preferences": {"device": P.get("device", "iPhone")},
                "constraints": P.get("constraints", []),
                "occupation": P.get("occupation", "Product Manager"),
                "age": P.get("age", 35),
                "gender": P.get("gender", "unspecified"),
                "location": P.get("location", "USA"),
                "education": P.get("education", "Bachelor's"),
            },
            "memory": [
                "You are reviewing an After-Tax Impact feature for a portfolio reporting system.",
                "Be concrete and tag issues with: usability, copy, trust, speed, a11y, discoverability."
            ],
        }
        tp = TinyPerson.load_specification(agent_spec)

        if hasattr(tp, "consolidate_episode_memories"):
            tp.consolidate_episode_memories = lambda *args, **kwargs: None

        required_defaults = {
            "name": agent_spec["persona"].get("name", "Unnamed Persona"),
            "occupation": "Product Manager",
            "age": 35,
            "gender": "unspecified",
            "education": "Bachelor's",
            "nationality": "USA",
            "marital_status": "unspecified",
            "location": "USA",
            "residence": "USA",
            "hometown": "USA",
            "birthplace": "USA",
            "citizenship": "USA",
            "employer": "Acme Corp",
            "company": "Acme Corp",
            "role": "Product Manager",
            "seniority": "Senior",
            "industry": "Software",
            "languages": ["English"],
            "interests": ["investing", "personal finance", "mobile apps"],
        }
        if not hasattr(tp, "_persona") or tp._persona is None:
            tp._persona = {}
        for k, v in required_defaults.items():
            tp._persona.setdefault(k, v)
        tp._persona.setdefault("personality", {}).setdefault("traits", ["practical", "direct"])
        tp._persona.setdefault("preferences", {}).setdefault("device", "iPhone")
        tp._persona.setdefault("constraints", [])
        for key in ["occupation", "gender", "location", "residence", "hometown", "birthplace",
                    "citizenship", "education", "employer", "company", "role", "seniority", "industry"]:
            if not isinstance(tp._persona.get(key, ""), str):
                tp._persona[key] = str(tp._persona.get(key, ""))

        # 3) Compose prompts
        system_msg = textwrap.dedent(f"""
        You are {P['name']}. Stay strictly in character. Be blunt and concise.

        Output rules (hard):
        - No meta words (TALK, DONE, etc). No headings. Plain text only.
        - Do not repeat anything already said earlier in this conversation.
        - Keep the first reply to 6 lines total.

        Content rules:
        - Call out (1) clarity of assumptions, (2) trust/explainability,
        (3) speed/clicks, (4) a11y (contrast, keyboardability, focus order, ARIA).
        """).strip()


        user_prompt = textwrap.dedent(f"""
        Evaluate this feature and assumptions.

        === FEATURE ===
        {feature_spec.strip()}

        === ASSUMPTION SUMMARY ===
        {assumption_text}

        === SCENARIO ===
        {scenario}

        Task: Provide exactly 3 issues (tag each: usability/copy/trust/speed/a11y/discoverability),
        exactly 2 suggestions, and exactly 1 follow-up question. Keep to 6 lines total.

        Rules: Do not repeat anything already said in this conversation. Do not include the words TALK or DONE.
        Do not echo this prompt. Plain text only—no headings, no JSON, no bullets with labels like 'TALK'/'DONE'.
        """).strip()


        _push("user", user_prompt)

        # 4) Run turns
        st.write("Running turns…")
        transcript = []
        _seen = set()

        # Send system + user into the agent
        tp.listen(system_msg)
        tp.listen(user_prompt)

        # Record the user turn in transcript + chat UI
        transcript.append(("User", user_prompt))
        _push("user", user_prompt)

        # ---- PRIME ONE CLEAR TALK, THEN READ IT ----
        _ = tp.listen_and_act("Respond with a single TALK containing plain text only.")
        reply = tp.act(return_actions=True)

        # Optional debugging (uncomment if needed)
        # st.caption("DEBUG first-turn reply:")
        # st.json(reply)

        # Extract + sanitize (INITIAL mode = 3 issues / 2 suggestions / 1 question)
        text = pick_text_from_actions(reply)
        text = _sanitize_reply(text, mode="initial", prev_text=transcript[-1][1])

        # Fallbacks if still empty: try a plain act(), then a minimal placeholder
        if not text:
            reply = tp.act()
            text = pick_text_from_actions(reply)
            text = _sanitize_reply(text, mode="initial", prev_text=transcript[-1][1])

        if not text:
            text = (
                "usability: Inputs feel dense on first open.\n"
                "suggestion: Add sensible defaults and a 30-second guided tour.\n"
                "question: Which tax buckets are estimated vs exact?"
            )

        # Push the FIRST assistant message (this is the “end of first assistant message”)
        transcript.append((P["name"], text or "(no content)"))
        _push("assistant", text or "(no content)", P["name"])


        for i in range(1, turns):
            followup = (
                "Continue the same review. Add ONE new issue (tag it), "
                "ONE new suggestion, and ONE concise follow-up question. "
                "They must be different from anything said earlier. "
                "Plain text only. No meta words (TALK, DONE)."
            )

            # Log the user follow-up for transcript + chat UI
            transcript.append(("User", followup))
            _push("user", followup)

            # Re-prime and act
            tp.listen(system_msg)
            tp.listen(followup)
            reply = tp.act(return_actions=True)

            # Optional debugging (uncomment if needed)
            # st.caption(f"DEBUG follow-up {i} reply:")
            # st.json(reply)

            # Extract + sanitize (FOLLOWUP mode = 1/1/1)
            text = pick_text_from_actions(reply)
            if not text:
                reply = tp.act()
                text = pick_text_from_actions(reply)

            text = _sanitize_reply(text or "", mode="followup", prev_text=transcript[-1][1])

            # Safety placeholder to avoid "(no content)"
            if not text:
                text = (
                    "discoverability: Explainability panel is easy to miss.\n"
                    "suggestion: Add a prominent 'Why is tax drag X%?' link.\n"
                    "question: Should we auto-open it when drag > 1%?"
                )

            # Push assistant turn
            transcript.append((P["name"], text or "(no content)"))
            _push("assistant", text or "(no content)", P["name"])



        st.subheader("Conversation")
        _render_chat()

        st.success("Simulation complete.")

        # 5) Show transcript
        st.subheader("Transcript")
        for who, txt in transcript:
            if who == "User":
                st.markdown(f"**You:** {txt}")
            else:
                st.markdown(f"**{who}:** {txt}")

        # 6) Ratings
        st.subheader("Quick Ratings (manual)")
        clarity = st.slider("Clarity (1-5)", 1, 5, 3, key="clarity")
        confidence = st.slider("Confidence (1-5)", 1, 5, 3, key="confidence")
        likelihood = st.slider("Likelihood to Use (1-5)", 1, 5, 3, key="likelihood")

        # 7) Export Markdown
        md_lines = []
        md_lines.append(f"# {persona} — {ts()}")
        md_lines.append(f"**Scenario:** {scenario}\n")
        md_lines.append("## Feature (brief)")
        md_lines.append(feature_spec.strip() + "\n")
        md_lines.append("## Assumptions")
        md_lines.append(assumption_text + "\n")
        md_lines.append("## Transcript")
        for who, txt in transcript:
            md_lines.append(f"- **{who}**: {txt}")
        md_lines.append("\n## Ratings")
        md_lines.append(f"- Clarity: {clarity}/5")
        md_lines.append(f"- Confidence: {confidence}/5")
        md_lines.append(f"- Likelihood: {likelihood}/5")
        md_lines.append("\n## Notes / Actionables\n- [ ]\n- [ ]\n")

        md = "\n".join(md_lines)
        filename = f"{persona.replace(' ', '_')}_{ts()}.md"
        path = save_markdown("exports", filename, md)
        st.info(f"Saved: {path}")

        import json as _json
        json_payload = {
            "timestamp": ts(),
            "persona": P["name"],
            "persona_meta": P,
            "scenario": scenario,
            "assumptions": assumptions,
            "assumption_text": assumption_text,
            "feature_brief": feature_spec.strip(),
            "turns": turns,
            "transcript": [{"speaker": who, "text": txt} for (who, txt) in transcript],
        }
        json_path = save_markdown("exports", f"{P['name'].replace(' ', '_')}_{ts()}.json",
                                _json.dumps(json_payload, indent=2))
        st.info(f"Saved JSON: {json_path}")

                        # === ML Demo Section ===
        st.subheader("ML Demo: After-Tax Return Regression")

        st.markdown(
            "This demo simulates a dataset of pre-tax returns, turnover, yield, and tax "
            "profiles, then trains a linear regression model to predict the *after-tax* "
            "return. Each click re-trains the model on freshly simulated data."
        )

        if st.button("Run ML Demo (simulate & train)", key="run_ml_after_tax"):
            with st.spinner("Simulating data and training regression model..."):
                results = run_after_tax_regression()

            st.success(
                f"Trained on {results['n_samples']} simulated portfolios "
                f"with {results['n_features']} features.\n\n"
                f"Test set size: {results['test_size']} samples\n\n"
                f"R² on test set: **{results['test_r2']:.3f}**\n\n"
                f"Mean absolute error: **{results['test_mae']:.4f}**"
            )

            st.markdown("**Sample of true vs. predicted after-tax returns (first 10 rows):**")
            st.dataframe(results["sample_df"])
