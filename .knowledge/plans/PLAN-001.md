---
id: PLAN-001
type: plan
project: descriptive-exams
session: S10
date: 2026-06-03
status: COMPLETE
---

# PLAN-001: Multi-User Architecture

## Goal
Convert single-user (hardcoded "rahul") app to multi-user with Google OAuth, session management,
and per-user data isolation across ies.db, rbi.db, upsc.db.

## What Was Built
- `web/auth.py`: Google OAuth flow, session tokens (7-day), single-session enforcement
- `web/pages/0_Login.py`: OAuth login + callback handler
- `web/pages/10_Profile.py`: Profile + logout
- `web/db.py`: `require_user()`, `get_user_id()`, `init_user()`, `create_session()`, `validate_session()`
- `seeds/`: rbi_seed.db + upsc_seed.db for Railway first-boot
- Composite indexes on user_id + topic_id + exam_id for all user tables

## Navigation Architecture
`app.py` uses Streamlit's `st.navigation()` API (1.36+). Two branches:
- Unauthenticated: `[_login]`
- Authenticated: grouped nav {Dashboard, Study, Practice, Progress, Account}
`_authed = bool(st.session_state.get("session_token"))` evaluated at boot.

## Known Architectural Risk (discovered in AUDIT-001)
The `_authed` check creates a split-brain scenario: navigation is registered once at boot.
Any page transition that changes auth state mid-cycle must use `st.rerun()`, NOT `st.switch_page()`.
See NAV-001 pattern. BUG-001, BUG-002, BUG-003 all stem from this design choice.

## Railway Deployment
- `railway.toml` sets `[deploy] startCommand = "streamlit run web/app.py --server.port $PORT"`
- Data volume at `/app/data/` — persisted across deploys
- First-boot copies seed DBs if live DBs don't exist
- Railway SSH required for direct DB access: `railway ssh python scripts/X.py`
