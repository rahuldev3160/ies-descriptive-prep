"""English Practice — hybrid keyword auto-score + self-assessment rubric."""
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from db import get_conn, jl, track_page_time
from auth import require_user
from styles import apply_theme, chip, score_card_html
from scoring import score_answer, build_feedback, RUBRICS, compute_self_assess_score

st.set_page_config(page_title="English Practice · Descriptive Exams", layout="wide", page_icon="📝")
apply_theme()

EXAM_ID = "english_practice"

conn = get_conn()
user_id = require_user(conn)
track_page_time(conn, "English Practice")


# ── DB helpers ─────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def _load_types() -> list[dict]:
    from db import get_conn as _gc
    c = _gc()
    try:
        rows = c.execute(
            "SELECT type_id, type_name, description, section_labels_json, "
            "section_weights_json, rubric_type, sort_order "
            "FROM english_question_types WHERE exam_id=? ORDER BY sort_order",
            (EXAM_ID,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        c.close()


@st.cache_data(ttl=300, show_spinner=False)
def _load_questions(type_id: str) -> list[dict]:
    from db import get_conn as _gc
    c = _gc()
    try:
        rows = c.execute(
            "SELECT question_id, type_id, prompt_text, marks, word_guide_json, "
            "word_count_target, section_weights_json, intro_text, body_text, "
            "conclusion_text, difficulty, source_exam "
            "FROM english_questions WHERE exam_id=? AND type_id=? ORDER BY difficulty, question_id",
            (EXAM_ID, type_id)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        c.close()


def _load_keyword_schema(question_id: str) -> dict:
    rows = conn.execute(
        "SELECT section, keyword, variants_json, weight, keyword_type, fuzzy_threshold, penalty "
        "FROM english_keywords WHERE question_id=? AND exam_id=?",
        (question_id, EXAM_ID)
    ).fetchall()
    schema: dict = {"intro": {}, "body": {}, "conclusion": {}}
    for sec in schema:
        schema[sec] = {"required": [], "bonus": [], "negative": [], "phrases": []}
    for row in rows:
        sec = row["section"]
        ktype = row["keyword_type"]
        entry = {
            "canonical": row["keyword"],
            "variants": json.loads(row["variants_json"] or f'["{row["keyword"]}"]'),
            "weight": float(row["weight"] or 1),
            "fuzzy_threshold": float(row["fuzzy_threshold"] or 0.82),
        }
        if row["penalty"] is not None:
            entry["penalty"] = float(row["penalty"])
        schema[sec][ktype].append(entry)
    return schema


def _save_attempt(question_id: str, intro: str, body: str, conclusion: str,
                  auto_result: dict, self_checks: dict, self_score: float) -> None:
    sections = auto_result.get("sections", {})
    nailed   = [k for sec in sections.values() for k in sec.get("keywords_hit", [])]
    missed   = [k for sec in sections.values() for k in sec.get("keywords_missed", [])]
    conn.execute(
        "INSERT INTO english_attempts "
        "(attempt_id,exam_id,user_id,question_id,"
        "user_answer_intro,user_answer_body,user_answer_conclusion,"
        "word_count_intro,word_count_body,word_count_conclusion,"
        "score_intro,score_body,score_conclusion,auto_score,self_assess_score,"
        "keywords_matched_json,keywords_missed_json,self_assess_json,session_id) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            uuid.uuid4().hex[:12], EXAM_ID, user_id, question_id,
            intro, body, conclusion,
            len(intro.split()), len(body.split()), len(conclusion.split()),
            round(sections.get("intro", {}).get("score_pct", 0) / 10, 2),
            round(sections.get("body",  {}).get("score_pct", 0) / 10, 2),
            round(sections.get("conclusion", {}).get("score_pct", 0) / 10, 2),
            round(auto_result.get("overall_pct", 0) / 10, 2),
            round(self_score, 4),
            json.dumps(nailed),
            json.dumps(missed),
            json.dumps(self_checks),
            st.session_state.get("session_id", uuid.uuid4().hex[:8]),
        )
    )
    conn.commit()


# ── Session state ───────────────────────────────────────────────────────────────
if "eng_curr_type" not in st.session_state:
    st.session_state.eng_curr_type = "essay"
if "eng_curr_qid" not in st.session_state:
    st.session_state.eng_curr_qid = None
if "eng_last_result" not in st.session_state:
    st.session_state.eng_last_result = None  # {qid, auto, self_assess}
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]

# ── Load data ───────────────────────────────────────────────────────────────────
all_types = _load_types()
if not all_types:
    st.error(
        "No English practice questions found. "
        "Run `python3 scripts/seed_english_content.py` to seed initial content."
    )
    conn.close()
    st.stop()

type_map = {t["type_id"]: t for t in all_types}

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📝 English Practice")
    st.divider()

    type_options = {t["type_id"]: t["type_name"] for t in all_types}
    curr_type_idx = list(type_options.keys()).index(st.session_state.eng_curr_type) \
        if st.session_state.eng_curr_type in type_options else 0

    selected_type_id = st.selectbox(
        "Question Type",
        list(type_options.keys()),
        index=curr_type_idx,
        format_func=lambda x: type_options[x],
    )
    if selected_type_id != st.session_state.eng_curr_type:
        st.session_state.eng_curr_type = selected_type_id
        st.session_state.eng_curr_qid = None
        st.session_state.eng_last_result = None
        st.rerun()

    questions = _load_questions(selected_type_id)
    if not questions:
        st.warning(f"No questions yet for {type_options[selected_type_id]}.")
        conn.close()
        st.stop()

    q_label_map = {
        q["question_id"]: f"{(q['source_exam'] or '').upper().replace('_',' ')} · "
                          f"{q['difficulty'].capitalize()} · "
                          f"{q['prompt_text'][:55]}…"
        for q in questions
    }
    qids = list(q_label_map.keys())

    curr_qid = st.session_state.eng_curr_qid
    if curr_qid not in qids:
        curr_qid = qids[0]
        st.session_state.eng_curr_qid = curr_qid

    selected_qid = st.selectbox(
        "Question",
        qids,
        index=qids.index(curr_qid),
        format_func=lambda x: q_label_map[x],
    )
    if selected_qid != st.session_state.eng_curr_qid:
        st.session_state.eng_curr_qid = selected_qid
        st.session_state.eng_last_result = None
        st.rerun()

    st.divider()
    qt_info = type_map.get(selected_type_id, {})
    if qt_info.get("description"):
        st.markdown(
            f'<div style="font-size:0.78rem;color:#9AA0A6;line-height:1.5">'
            f'{qt_info["description"]}</div>',
            unsafe_allow_html=True,
        )

selected_q = next(q for q in questions if q["question_id"] == selected_qid)
qt_info     = type_map.get(selected_type_id, {})
rubric_type = qt_info.get("rubric_type", selected_type_id)
criteria    = RUBRICS.get(rubric_type, [])

sec_labels = json.loads(qt_info.get("section_labels_json") or
                        '{"intro":"Introduction","body":"Body","conclusion":"Conclusion"}')
sec_weights = json.loads(selected_q.get("section_weights_json") or
                         '{"intro":0.15,"body":0.70,"conclusion":0.15}')
word_guide  = json.loads(selected_q.get("word_guide_json") or
                         '{"intro":80,"body":340,"conclusion":80}')

# ── Question card ───────────────────────────────────────────────────────────────
diff_color = {"easy": "#81C995", "medium": "#FDD663", "hard": "#F28B82"}.get(
    selected_q.get("difficulty", "medium"), "#9AA0A6"
)
_marks_chip = (
    f'<span class="chip chip-purple" style="margin-left:6px">{selected_q["marks"]}m</span>'
    if selected_q["marks"] else ""
)
st.markdown(
    f'<div class="gem-card-accent">'
    f'<div style="margin-bottom:10px">'
    f'<span class="chip">{(selected_q["source_exam"] or "").upper().replace("_"," ")}</span>'
    f'<span class="chip" style="margin-left:6px;color:{diff_color}">'
    f'{(selected_q["difficulty"] or "medium").capitalize()}</span>'
    f'{_marks_chip}'
    f'</div>'
    f'<div style="font-size:0.98rem;line-height:1.7;color:#E8EAED;white-space:pre-wrap">'
    f'{selected_q["prompt_text"]}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Determine phase ─────────────────────────────────────────────────────────────
last = st.session_state.eng_last_result
phase = "write"
if last and last.get("qid") == selected_qid:
    phase = "done" if last.get("self_assess") is not None else "self_assess"


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Write
# ══════════════════════════════════════════════════════════════════════════════
if phase == "write":
    st.markdown(
        '<div style="font-size:0.78rem;color:#9AA0A6;margin-bottom:12px">'
        'Score is keyword coverage (auto) + structure check (self-assessed). '
        'No AI required — instant results.</div>',
        unsafe_allow_html=True,
    )
    with st.form(f"eng_form_{selected_qid}", clear_on_submit=False):
        for sec, label in sec_labels.items():
            wg = word_guide.get(sec, 80)
            color = {"intro": "#8AB4F8", "body": "#C084FC", "conclusion": "#81C995"}[sec]
            placeholder_map = {
                "intro": f"~{wg} words",
                "body":  f"~{wg} words",
                "conclusion": f"~{wg} words",
            }
            if selected_type_id == "précis" and sec == "intro":
                placeholder_map["intro"] = "Give a title — max 10 words"
            elif selected_type_id == "précis" and sec == "conclusion":
                placeholder_map["conclusion"] = "[Word count: N] — state your word count here"
            elif selected_type_id == "rc" and sec == "intro":
                placeholder_map["intro"] = "~50 words · State the direct answer first"

            height = 50 if (selected_type_id == "précis" and sec in ("intro", "conclusion")) else \
                     80  if sec == "intro" else \
                     260 if sec == "body" else 90
            st.markdown(
                f'<div class="section-header" style="color:{color}">{label}</div>',
                unsafe_allow_html=True,
            )
            st.text_area(
                "", height=height,
                key=f"eng_{sec}_{selected_qid}",
                placeholder=placeholder_map[sec],
                label_visibility="collapsed",
                max_chars=3000,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "Score My Answer →", type="primary", use_container_width=True
        )

    if submitted:
        intro_ans = st.session_state.get(f"eng_intro_{selected_qid}", "").strip()
        body_ans  = st.session_state.get(f"eng_body_{selected_qid}", "").strip()
        conc_ans  = st.session_state.get(f"eng_conclusion_{selected_qid}", "").strip()

        if not body_ans:
            st.warning("Please write at least a Body section before scoring.")
            st.stop()

        kw_schema = _load_keyword_schema(selected_qid)
        raw_result = score_answer(kw_schema, sec_weights, intro_ans, body_ans, conc_ans)
        feedback   = build_feedback(raw_result)

        st.session_state.eng_last_result = {
            "qid":         selected_qid,
            "intro":       intro_ans,
            "body":        body_ans,
            "conclusion":  conc_ans,
            "auto":        feedback,
            "self_assess": None,
        }
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — Auto-score shown + self-assessment rubric
# ══════════════════════════════════════════════════════════════════════════════
elif phase == "self_assess":
    auto = last["auto"]

    st.markdown('<div class="section-header">Keyword Coverage</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, (label, sec_key) in zip(
        [sc1, sc2, sc3, sc4],
        [(sec_labels["intro"], "intro"), (sec_labels["body"], "body"),
         (sec_labels["conclusion"], "conclusion"), ("Overall", None)],
    ):
        with col:
            score = (auto["overall_pct"] / 10) if sec_key is None else \
                    (auto["sections"][sec_key]["score_pct"] / 10)
            st.markdown(score_card_html(label, score), unsafe_allow_html=True)

    if auto.get("nailed"):
        st.markdown("<br>", unsafe_allow_html=True)
        hits_html = " ".join(
            f'<span class="chip chip-green">{k}</span>' for k in auto["nailed"][:6]
        )
        st.markdown(f'<div>✅ <strong>Covered:</strong> {hits_html}</div>', unsafe_allow_html=True)
    if auto.get("missing"):
        missed_html = " ".join(
            f'<span class="chip" style="color:#F28B82;border-color:#F28B8244">{k}</span>'
            for k in auto["missing"][:6]
        )
        st.markdown(f'<div>❌ <strong>Missing:</strong> {missed_html}</div>', unsafe_allow_html=True)

    # Per-section hints
    with st.expander("Section hints", expanded=False):
        for sec, label in sec_labels.items():
            hint = auto["sections"][sec]["hint"]
            if hint:
                st.markdown(
                    f'<div style="padding:4px 0;font-size:0.85rem">'
                    f'<span class="chip">{label}</span> {hint}</div>',
                    unsafe_allow_html=True,
                )

    # Word count compliance (Précis)
    if selected_type_id == "précis" and selected_q.get("word_count_target"):
        target = selected_q["word_count_target"]
        actual = len(last["body"].split())
        pct_off = abs(actual - target) / target * 100
        wc_ok = pct_off <= 10
        wc_color = "#81C995" if wc_ok else "#FDD663" if pct_off <= 25 else "#F28B82"
        st.markdown(
            f'<div style="margin-top:8px;font-size:0.85rem">'
            f'<span class="chip" style="color:{wc_color}">'
            f'Word count: {actual} / {target} target '
            f'({"✓ within ±10%" if wc_ok else f"{pct_off:.0f}% off — aim for {target}±{int(target*0.1)} words"})'
            f'</span></div>',
            unsafe_allow_html=True,
        )

    # Model answer reveal
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="section-header">Model Answer</div>', unsafe_allow_html=True)
    for sec, label in sec_labels.items():
        model_text = selected_q.get(f"{sec}_text") or ""
        if model_text:
            with st.expander(label, expanded=(sec == "body")):
                color = {"intro": "#8AB4F844", "body": "#C084FC44", "conclusion": "#81C99544"}[sec]
                st.markdown(
                    f'<div class="answer-section" style="border-left:3px solid {color};'
                    f'padding:10px 14px;border-radius:6px;line-height:1.7">'
                    f'{model_text}</div>',
                    unsafe_allow_html=True,
                )

    # Self-assessment rubric
    st.divider()
    st.markdown('<div class="section-header">Structure Check</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.80rem;color:#9AA0A6;margin-bottom:12px">'
        'Review the model answer above, then honestly mark which criteria your answer met.</div>',
        unsafe_allow_html=True,
    )

    with st.form("eng_self_assess_form"):
        checks: dict[str, bool] = {}
        for criterion in criteria:
            checks[criterion["id"]] = st.checkbox(
                criterion["text"],
                key=f"sa_{criterion['id']}_{selected_qid}",
            )
        st.markdown("<br>", unsafe_allow_html=True)
        completed = st.form_submit_button(
            "Complete Assessment →", type="primary", use_container_width=True
        )

    if completed:
        self_score = compute_self_assess_score(rubric_type, checks)
        try:
            _save_attempt(
                selected_qid,
                last["intro"], last["body"], last["conclusion"],
                auto, checks, self_score,
            )
        except Exception as _e:
            st.toast(f"Could not save attempt: {_e}", icon="⚠️")

        last["self_assess"] = {"checks": checks, "score": self_score}
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — Final view
# ══════════════════════════════════════════════════════════════════════════════
elif phase == "done":
    auto         = last["auto"]
    self_assess  = last["self_assess"]
    self_score   = self_assess.get("score", 0.0)
    checks       = self_assess.get("checks", {})

    st.markdown('<div class="section-header">Your Results</div>', unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        auto_pct = auto["overall_pct"]
        auto_color = "#81C995" if auto_pct >= 70 else "#FDD663" if auto_pct >= 45 else "#F28B82"
        st.markdown(
            f'<div class="gem-card" style="text-align:center">'
            f'<div style="font-size:0.78rem;color:#9AA0A6;margin-bottom:4px">Keyword Coverage</div>'
            f'<div style="font-size:2rem;font-weight:700;color:{auto_color}">{auto_pct:.0f}%</div>'
            f'<div style="font-size:0.75rem;color:#9AA0A6">{auto["grade"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with r2:
        sa_pct = round(self_score * 100, 0)
        sa_total = len(criteria)
        sa_met   = sum(1 for c in criteria if checks.get(c["id"], False))
        sa_color = "#81C995" if self_score >= 0.70 else "#FDD663" if self_score >= 0.45 else "#F28B82"
        st.markdown(
            f'<div class="gem-card" style="text-align:center">'
            f'<div style="font-size:0.78rem;color:#9AA0A6;margin-bottom:4px">Structure Quality</div>'
            f'<div style="font-size:2rem;font-weight:700;color:{sa_color}">{sa_met}/{sa_total}</div>'
            f'<div style="font-size:0.75rem;color:#9AA0A6">{sa_pct:.0f}% criteria met</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Keyword breakdown tabs
    tab_i, tab_b, tab_c = st.tabs([sec_labels["intro"], sec_labels["body"], sec_labels["conclusion"]])
    for tab, sec_key in [(tab_i, "intro"), (tab_b, "body"), (tab_c, "conclusion")]:
        with tab:
            sec_fb = auto["sections"][sec_key]
            sc1_, sc2_ = st.columns(2)
            with sc1_:
                if sec_fb["keywords_hit"]:
                    st.markdown("**Covered**")
                    for k in sec_fb["keywords_hit"]:
                        st.markdown(
                            f'<div style="color:#81C995;font-size:0.85rem;padding:2px 0">✅ {k}</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown('<div style="color:#9AA0A6;font-size:0.85rem">No required keywords matched.</div>',
                                unsafe_allow_html=True)
            with sc2_:
                if sec_fb["keywords_missed"]:
                    st.markdown("**Missing**")
                    for k in sec_fb["keywords_missed"]:
                        st.markdown(
                            f'<div style="color:#F28B82;font-size:0.85rem;padding:2px 0">❌ {k}</div>',
                            unsafe_allow_html=True,
                        )
            if sec_fb.get("misconceptions"):
                st.markdown("**Misconceptions flagged**")
                for m in sec_fb["misconceptions"]:
                    st.markdown(
                        f'<div style="color:#FDD663;font-size:0.85rem;padding:2px 0">⚠️ {m}</div>',
                        unsafe_allow_html=True,
                    )
            st.markdown(
                f'<div style="margin-top:8px;font-size:0.80rem;color:#9AA0A6">{sec_fb["hint"]}</div>',
                unsafe_allow_html=True,
            )

    # Structure criteria summary
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Structure criteria detail", expanded=False):
        for c in criteria:
            met = checks.get(c["id"], False)
            icon = "✅" if met else "❌"
            st.markdown(
                f'<div style="padding:3px 0;font-size:0.85rem">{icon} {c["text"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div style="font-size:0.75rem;color:#9AA0A6;margin-top:8px">'
        'Keyword coverage = content score. Structure quality = format and argument score. '
        'A correct paraphrase that uses no tagged keywords may still score low — that is the known '
        'limitation of keyword scoring. Use the model answer as your benchmark.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    nav1, nav2 = st.columns(2)
    with nav1:
        if st.button("↩ Retry this question", use_container_width=True):
            st.session_state.eng_last_result = None
            st.rerun()
    with nav2:
        qids = [q["question_id"] for q in questions]
        next_qid = qids[(qids.index(selected_qid) + 1) % len(qids)]
        if st.button("Next Question →", type="primary", use_container_width=True):
            st.session_state.eng_curr_qid = next_qid
            st.session_state.eng_last_result = None
            st.rerun()

conn.close()
