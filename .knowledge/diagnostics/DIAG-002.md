---
id: DIAG-002
type: diagnostic
project: descriptive-exams
session: S13
date: 2026-06-05
status: RESOLVED
resolution: BUG-001
---

# DIAG-002: Production "Page not found" on Login

## Symptom
User sees "Sign-in failed: Could not find page: pages/Dashboard.py" after Google OAuth redirect.
Streamlit "Page not found" modal also appears simultaneously.

## Investigation Steps
1. Confirmed Dashboard.py exists at web/pages/Dashboard.py (committed in c050ab9)
2. Checked git status — file was committed and pushed
3. Read auth.py, app.py, 0_Login.py
4. Found: st.switch_page("pages/Dashboard.py") called when navigation only had [_login] registered

## Root Cause
NAV-001 pattern — see BUG-001.

## Resolution
Replaced st.switch_page() with st.rerun() in 0_Login.py. Deployed commit 0fec71e.
