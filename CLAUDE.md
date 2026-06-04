# CLAUDE.md — Descriptive Exams Project

## Knowledge Base — ALWAYS CHECK FIRST
Before any audit, bug investigation, or architecture review:
1. Read `.knowledge/INDEX.md` — scan open bugs and past audits
2. Read `~/.claude/knowledge/patterns/PATTERNS.md` — check for known patterns before investigating from scratch

## Knowledge Base — ALWAYS UPDATE AFTER
After any of these task types, write synthesized records to `.knowledge/` before finishing the response:
- Multi-agent analysis or audit
- Significant bug investigation and fix (>1 file changed)
- Architecture review or plan
- Deployment diagnostic
- Any task that consumed >5,000 tokens

**What to write:** Synthesized findings only — not raw agent output. One record per bug/audit/plan.
**Where:** `.knowledge/bugs/`, `.knowledge/audits/`, `.knowledge/plans/`, `.knowledge/diagnostics/`
**Always:** Update `.knowledge/INDEX.md` to reflect the new/changed records.

## Environment
- Python: `/opt/homebrew/bin/streamlit` (Python 3.11). Never use `/Library/Python/3.9/`
- App entry point: `streamlit run web/app.py`
- DB files: `data/ies.db`, `data/rbi.db`, `data/upsc.db`
- Seeds: `seeds/ies_seed.db`, `seeds/rbi_seed.db`, `seeds/upsc_seed.db`
- Production: `ies-descriptive-prep-production.up.railway.app`
- Railway SSH: `railway ssh python scripts/X.py` (not `railway run`)

## Architecture Constraints
- Streamlit navigation uses `st.navigation()` (1.36+ API). Auth-conditional branches.
- **CRITICAL**: Never use `st.switch_page()` to cross nav branches. Use `st.rerun()` instead.
  See NAV-001 pattern and BUG-001, BUG-002, BUG-003.
- All user data is scoped by `user_id` (UUID). Never trust `get_user_id()` alone — use `require_user(conn)`.
- DB connections: opened with `get_conn()`, must be closed. Use try/finally in pages (BUG-007 pending fix).

## Code Style
- No comments unless WHY is non-obvious
- No trailing summary in responses — Rahul can read the diff
- Explain technical concepts with analogies when building/debugging (see memory)
- Use parallel tool calls wherever independent
