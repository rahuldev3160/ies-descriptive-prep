"""Answer Review — AI feedback on written answers against examiner rubric. Pro feature."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from auth import require_user
from db import get_conn, track_page_time
from styles import apply_theme

st.set_page_config(page_title="Answer Review · Exam Prep", layout="centered", page_icon="🔒")
apply_theme()

conn = get_conn()
user_id = require_user(conn)
track_page_time(conn, "Answer Review")

# Check subscription tier
row = conn.execute(
    "SELECT subscription_tier FROM users WHERE user_id=?", (user_id,)
).fetchone()
is_pro = row and row["subscription_tier"] == "pro"

st.markdown("## 🔒 Answer Review")
st.markdown(
    '<div style="color:#9AA0A6;font-size:0.88rem;margin-bottom:1.5rem">'
    'Submit your written exam answer and get detailed AI feedback scored against '
    'the examiner\'s rubric.</div>',
    unsafe_allow_html=True,
)

if is_pro:
    # Placeholder — actual feature not built yet
    st.info("Pro access confirmed. This feature is coming soon — check back shortly.")
else:
    st.markdown(
        '<div style="background:#1C2B3A;border:1px solid #C084FC33;border-radius:12px;'
        'padding:32px 28px;text-align:center;max-width:520px;margin:0 auto">'
        '<div style="font-size:2.5rem;margin-bottom:12px">🔒</div>'
        '<div style="color:#E8EAED;font-weight:700;font-size:1.15rem;margin-bottom:10px">'
        'Pro Feature</div>'
        '<div style="color:#9AA0A6;font-size:0.9rem;line-height:1.6;margin-bottom:20px">'
        'Write your exam answer, paste it here, and receive a detailed score against the '
        'examiner\'s rubric — covering argument structure, key concepts, diagrams, '
        'and conclusion quality.<br><br>'
        'Available for IES, RBI DEPR, and UPSC Economics Optional questions.</div>'
        '<div style="color:#C084FC;font-size:0.8rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:.07em">Coming soon — Pro plan</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#9AA0A6;font-size:0.82rem">'
        'Until then, you can do this manually:<br>'
        'paste your answer into Claude or Gemini and ask it to score your answer '
        'against an IES examiner rubric.</div>',
        unsafe_allow_html=True,
    )

conn.close()
