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

# Quiet a noisy pydantic warning some users see
warnings.filterwarnings("ignore", message=".*UnsupportedFieldAttributeWarning.*")

# 1) Load env
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="TinyTroupe Persona Simulator", layout="wide")
st.title("TinyTroupe Persona Simulator — After-Tax Impact (Draft)")

# 2) UI layout
col1, col2 = st.columns([1, 2])

with col1:
    # Personas
    personas = load_personas("app/personas.json")
    persona_names = [p["name"] for p in personas]
    persona = st.selectbox("Persona", persona_names)

    # Assumptions (these drive your "portfolio tax impact" scenario)
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

    # Feature brief from file, but editable in the UI
    feature_spec = st.text_area(
        "Feature Brief (edit as needed)",
        height=220,
        value=open("app/feature_presets.md", "r", encoding="utf-8").read()
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

# Build assumptions dict + summary (used in prompt and export)
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
# 👉 assumption_text is the human-readable summary we’ll send to the persona
assumption_text = assumption_summary(assumptions)

with col2:
    st.subheader("Run Simulation")
    if not OPENAI_KEY:
        st.warning("OPENAI_API_KEY not found. Create .env in the project root and restart the app.")

    if st.button("Simulate"):
        # 1) Get the chosen persona spec from personas.json
        P = [p for p in personas if p["name"] == persona][0]

        # 2) Build the TinyPerson from a spec (most robust path across versions)
        agent_spec = {
            "type": "TinyPerson",
            "persona": {
                "name": P.get("name", "Unnamed Persona"),
                "biography": P.get("biography", "No biography provided."),
                "personality": {"traits": P.get("traits", ["practical", "direct"])},
                "preferences": {"device": P.get("device", "iPhone")},
                "constraints": P.get("constraints", []),

                # ✅ Add robust defaults to avoid KeyError in TinyTroupe internals
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

        # --- Hard disable episodic memory consolidation to avoid Document.text errors ---
        if hasattr(tp, "consolidate_episode_memories"):
            tp.consolidate_episode_memories = lambda *args, **kwargs: None

        # --- Harden persona for TT internals that assume certain fields exist ---
        # Add generous defaults to avoid KeyErrors from minibio/memory steps.
        required_defaults = {
            # common basic facts
            "name": agent_spec["persona"].get("name", "Unnamed Persona"),
            "occupation": "Product Manager",
            "age": 35,
            "gender": "unspecified",
            "education": "Bachelor's",
            "nationality": "USA",
            "marital_status": "unspecified",
            # geo / identity variants TinyTroupe may reference
            "location": "USA",
            "residence": "USA",        # ← your current KeyError
            "hometown": "USA",
            "birthplace": "USA",
            "citizenship": "USA",
            # other commonly used fields in bios
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

        # Ensure top-level defaults exist
        for k, v in required_defaults.items():
            tp._persona.setdefault(k, v)

        # Ensure nested structures exist
        tp._persona.setdefault("personality", {}).setdefault("traits", ["practical", "direct"])
        tp._persona.setdefault("preferences", {}).setdefault("device", "iPhone")
        tp._persona.setdefault("constraints", [])

        # Make sure stringy fields are strings (some TT code assumes str)
        for key in ["occupation", "gender", "location", "residence", "hometown", "birthplace",
                    "citizenship", "education", "employer", "company", "role", "seniority", "industry"]:
            if not isinstance(tp._persona.get(key, ""), str):
                tp._persona[key] = str(tp._persona.get(key, ""))


        # 3) Compose the initial prompt
        # NOTE:
        #  - feature_spec.strip() is just the *trimmed* text from the big text area above.
        #  - assumption_text is the nicely formatted summary we built right before (from the sliders).
        system_msg = textwrap.dedent(f"""
        You are {P['name']}. Stay strictly in character.
        Be blunt and concrete. Always call out:
        (1) clarity of assumptions, (2) trust/explainability,
        (3) speed/clicks, (4) a11y with WCAG cues if relevant
        (contrast ratios, keyboardability, focus order, ARIA live regions).
        """).strip()

        user_prompt = textwrap.dedent(f"""
        Evaluate this feature and assumptions.

        === FEATURE ===
        {feature_spec.strip()}

        === ASSUMPTION SUMMARY ===
        {assumption_text}

        === SCENARIO ===
        {scenario}

        Task: Provide 3 specific issues (tag each with one of:
        usability, copy, trust, speed, a11y, discoverability),
        2 concrete suggestions, and 1 follow-up question.
        """).strip()

        # 4) Run a few conversational "turns" using TinyTroupe actions directly
        st.write("Running turns…")
        transcript = []

        # Seed the "system" and initial prompt into the agent's message buffer
        tp.listen(system_msg)
        tp.listen(user_prompt)
        transcript.append(("User", user_prompt))

        def pick_text_from_actions(payload) -> str:
            """
            Best-effort text extractor for TinyTroupe responses.
            It handles:
            - {"action": {"type": "TALK", "content": "..."}}
            - {"action": "TALK", "content": "..."}
            - {"content": "..."} / {"text": "..."} / {"message": "..."}
            - lists/tuples of the above
            - nested {"data": ...} / {"payload": ...}
            - plain strings

            Returns a single plain-text string (may be multiline).
            """

            texts: list[str] = []

            def visit(obj):
                # None
                if obj is None:
                    return

                # String
                if isinstance(obj, str):
                    s = obj.strip()
                    if s:
                        texts.append(s)
                    return

                # List/Tuple: visit each item
                if isinstance(obj, (list, tuple)):
                    for item in obj:
                        visit(item)
                    return

                # Dict-like
                if isinstance(obj, dict):
                    # 1) direct human-texty keys
                    for k in ("content", "text", "message"):
                        v = obj.get(k)
                        if isinstance(v, str) and v.strip():
                            texts.append(v.strip())

                    # 2) nested or flat action envelope
                    if "action" in obj:
                        a = obj["action"]
                        if isinstance(a, dict):
                            act_type = str(a.get("type", "")).upper()
                            c = a.get("content") or a.get("text") or ""
                        else:
                            act_type = str(a).upper()
                            c = obj.get("content") or obj.get("text") or ""

                        if act_type in {"TALK", "SAY", "SPEAK", "REPLY"} and isinstance(c, str) and c.strip():
                            texts.append(c.strip())

                    # 3) sometimes text is nested under data/payload
                    for k in ("data", "payload"):
                        if k in obj:
                            visit(obj[k])

                    return

                # Fallback: try model_dump()/dict()/__dict__
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
                        visit({k: v for k, v in d.items() if not k.startswith("_")})
                        return
                    except Exception:
                        pass

                # Last resort: ignore (don’t stringify unknown objects)

            visit(payload)
            return "\n".join([t for t in texts if t])




        # --- First response: prefer structured action payloads ---
        reply = tp.act(return_actions=True)        # ① ask for actions first
        text  = pick_text_from_actions(reply)

        if not text:
            reply = tp.act()                       # ② maybe plain text
            text  = pick_text_from_actions(reply)  # (handles strings too)

        if not text:
            reply = tp.listen_and_act(             # ③ force a TALK/SAY turn
                "Reply with a single TALK action whose content is plain text (no JSON). "
                "Provide 3 issues (tagged), 2 suggestions, and 1 follow-up question."
            )
            text = pick_text_from_actions(reply)

        # Optional on-screen debug when nothing parsed
        if not text:
            st.caption("Raw reply (debug):")
            st.code(repr(reply))

        transcript.append((P["name"], text or "(no content)"))


        # --- Follow-up turns ---
        for i in range(1, turns):
            followup = (
                "Add one NEW issue (tagged: usability/copy/trust/speed/a11y/discoverability), "
                "one NEW suggestion, and one concise follow-up question. Answer in plain text (no JSON)."
            )
            transcript.append(("User", followup))
            tp.listen(followup)

            # force a TALK/SAY; this makes 0.5.x much more reliable
            reply = tp.listen_and_act(
                "Respond now with a single TALK action (plain text only): "
                "one new tagged issue, one new suggestion, one concise follow-up question."
            )
            text = pick_text_from_actions(reply)

            if not text:
                reply = tp.act(return_actions=True)    # inspect action buffer if needed
                text  = pick_text_from_actions(reply)

            if not text:
                reply = tp.act()                       # last fallback
                text  = pick_text_from_actions(reply)

            if not text:
                st.caption("Raw follow-up reply (debug):")
                st.code(repr(reply))

            transcript.append((P["name"], text or "(no content)"))

            if not text:
                st.caption("Raw reply (debug):")
                st.code(repr(reply))



        st.success("Simulation complete.")

        # 5) Show transcript in Streamlit
        st.subheader("Transcript")
        for who, text in transcript:
            if who == "User":
                st.markdown(f"**You:** {text}")
            else:
                st.markdown(f"**{who}:** {text}")

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
        for who, text in transcript:
            md_lines.append(f"- **{who}**: {text}")
        md_lines.append("\n## Ratings")
        md_lines.append(f"- Clarity: {clarity}/5")
        md_lines.append(f"- Confidence: {confidence}/5")
        md_lines.append(f"- Likelihood: {likelihood}/5")
        md_lines.append("\n## Notes / Actionables\n- [ ]\n- [ ]\n")

        md = "\n".join(md_lines)
        filename = f"{persona.replace(' ', '_')}_{ts()}.md"
        path = save_markdown("exports", filename, md)
        st.info(f"Saved: {path}")

