# PLAN-013 — S25: nyaya.db canonical identity + event store

**Date:** 2026-06-06 | **Status:** Phase 2 complete (Phase 3 pending)

## Motivation
3 existing DBs (ies/rbi/upsc) are exam-scoped. No shared identity store meant:
- Cross-product user lookup requires JOINs across separate SQLite files (impossible)
- Events scattered in ies.db even for RBI/UPSC actions
- No foundation for Nyaya Recall or Nyaya Atlas to share user context

## Architecture Decision
Add `nyaya.db` as a 4th DB — canonical identity + event store for all NYAYA products.

**Canonical tables in nyaya.db:**
- `users` — identity, profile, onboarding, subscription tier
- `sessions` — auth tokens (moved from ies.db)
- `user_events` — all behavioural events across all exams/products
- `product_enrollments` — which products a user is enrolled in

**Exam DBs (ies/rbi/upsc) keep:** syllabus, questions, answers, rubrics, attempts, mastery. User scoping by user_id still works — no FK to nyaya.db (SQLite can't cross-file FK).

## Phase 1 — Completed (S25, commit pre-9a26646)
- Fixed 3 Phase 1 bugs:
  - session_id was `flask_session.get("user_id", uid)` → now `flask_session.get("session_id") or uid`
  - `track_page_time()` had `uid == USER_ID` guard blocking all auth'd prod users
  - rbi.db had `DEFAULT 'rahul'` on user_id columns (m011 recreation migration)
- Added `session["session_id"] = str(uuid4())` on login (auth_bp.py)

## Phase 2 — Completed (S25, commit 9a26646)
Files changed: db.py, app.py, auth_bp.py, setup_bp.py, dashboard_bp.py, progress_bp.py, feedback_bp.py, scripts/migrate.py, migrations/m012_init_nyaya_schema.py, seeds/nyaya_seed.db

**Key routing changes:**
- `g.nyaya_conn` opened per request in app.py `before_request`; closed in `teardown_appcontext`
- `validate_session(g.nyaya_conn, token)` — auth validates against nyaya.db
- `upsert_user(g.nyaya_conn, ...)` + `create_session(g.nyaya_conn, ...)` — auth writes to nyaya.db
- `log_event()` ignores `conn` arg, always writes to nyaya.db via `get_nyaya_conn()`
- `save_onboarding()` / `get_study_path()` use nyaya.db as canonical user-profile store
- `dashboard_bp` reads `onboarding_completed` + `exam_focus` from nyaya.db
- `progress_bp` reads `subscription_tier` from nyaya.db
- `feedback_bp` replaces cross-DB JOIN with two-query Python merge

**Migration:** m012_init_nyaya_schema.py creates tables + copies OAuth users/sessions/events from ies.db.
nyaya.db bootstrapped from seeds/nyaya_seed.db on first Railway deploy (BOOTSTRAP_DBS pattern).

## Phase 3 — Pending
- Add phone_number to nyaya.db users; fully migrate profile_bp.py to nyaya_conn
- Add streak tracking (streak_current, streak_longest, last_practice_date)
- Add first_ai_eval_at / activation_completed to users (aha moment tracking)
- Wire quiz_session_completed events in rbi_prep_bp + drop rbi_sessions table
- Build progress aggregation query (accuracy trend, syllabus %, days-until-exam)
- rbi_sessions table: 0 rows despite 9 rbi_attempts — fix session tracking

## Cross-DB JOIN Pattern
SQLite cannot JOIN across separate .db files. Pattern for cross-DB user lookups:
```python
# Step 1: fetch rows from ies.db
rows = conn.execute("SELECT * FROM user_feedback ORDER BY created_at DESC").fetchall()
# Step 2: fetch user info from nyaya.db
user_ids = list({r["user_id"] for r in rows})
user_rows = nyaya_conn.execute(f"SELECT user_id, display_name, email FROM users WHERE user_id IN ({','.join('?'*len(user_ids))})", user_ids).fetchall()
users_map = {r["user_id"]: r for r in user_rows}
# Step 3: Python merge
merged = [{**dict(r), "display_name": users_map.get(r["user_id"], {}).get("display_name")} for r in rows]
```
