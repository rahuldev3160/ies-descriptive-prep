# Descriptive Exams — Session Handoff

## Last Updated
2026-06-06 (Session 19 — COMPLETE)

---

## Session 19 Summary (2026-06-06)

### English dashboard UX fixes

Three gaps fixed in `web/blueprints/english_bp.py` + `web/templates/english_dashboard.html` + `web/templates/english.html`:
- Recent attempts showed raw hex question_id codes → fixed by JOINing `english_questions` to pull `prompt_text`, now displayed truncated + linked
- Practice cards showed no attempt count → added `attempt_counts` dict (keyed by `type_id`) passed to template; green "N done" chip rendered when `attempt_counts[type.type_id] > 0`
- No back-link from practice page to dashboard → added "← English Dashboard" breadcrumb at top of `english.html`

### Feedback feature — end-to-end

New files: `web/blueprints/feedback_bp.py`, `web/templates/feedback.html`

- `user_feedback` table created in `_FEEDBACK_TABLE_SQL` migration in `app.py`, called in `create_app()`
- `GET /feedback`: queries `user_feedback JOIN users`, renders sorted feedback list with colored left-border cards and status badges
- `POST /feedback/submit`: validates title not empty, inserts, flash + redirect (PRG pattern)
- 4 categories: Bug (`#F28B82`), Feature Request (`#8AB4F8`), Issue (`#FDD663`), Other (`#9AA0A6`)
- 3 statuses: open, acknowledged, resolved — all color-coded
- Registered as `feedback_bp` in `app.py`; sidebar link added under "Track & Account" in `base.html`

### RBI dashboard redesign

Complete rewrite of `web/templates/rbi_dashboard.html` + `web/blueprints/rbi_dashboard_bp.py`:
- **`rbi_key_data` DB table** (40 items, 6 sections) seeded on startup via `_run_rbi_migrations()` in `app.py` using `INSERT OR IGNORE` (idempotent). `is_must_know=1` on 6 items.
- **Must-Know panel** (left column): 6 facts inline + `<details>` expand to all 40 grouped by section
- **My Progress panel** (right column): 4 stat cards (Mastery, Readiness, Qs Attempted, Topics ≥50%) + `<details>` for subject bars
- **Subject Coverage**: 3 worst visible + `<details>` expand to all
- **Top Gaps**: 3 worst visible + `<details>` expand to remaining
- **Action buttons**: Priority 1 MCQs | Priority 2 Quiz | Full Key Data

### RBI Prep tab renames

In `web/templates/rbi_prep.html`:
- "Phase 1 Drill" → "Priority 1 MCQs" (all labels, empty states, score headings)
- "Tier 2 Quiz" → "Priority 2" (same thoroughness)
- Info-boxes added under each tab explaining what it contains

### Sidebar restructure

`web/templates/base.html` — 5 groups (16 links) → 3 groups (17 links):
- **Dashboards**: IES 2026, RBI Grade B, UPSC Mains, English
- **Study & Practice**: IES PYQ Answers, Study Brief, IES Quiz, IES Past Papers, RBI Priority 1, RBI Priority 2, UPSC Mains Topics, English Practice
- **Track & Account**: My Progress, Answer Review, Feedback, Setup, Profile, Sign Out

RBI Priority 1/2 links use query params (`?tab=phase1_drill`, `?tab=tier2_quiz`) to land on the right tab directly.

### CSS additions (`web/static/style.css`)

- `.expand-section` / `.expand-arrow` — styled `<details>/<summary>` toggle (blue arrow, rotates on open)
- `.dash-panel` — dashboard inline panel container
- `.dash-panel-title` — small uppercase panel label
- `.kd-row`, `.kd-name`, `.kd-value` — key data row layout

### Bugs fixed this session

- `rr_03` seed color typo: `"#C084PC"` → `"#C084FC"` in `web/app.py` `_RBI_KEY_DATA_SEED`

### Commit

`8841b84` — 15 files changed, 712 insertions(+), 124 deletions(−)
New files: `web/blueprints/feedback_bp.py`, `web/templates/feedback.html`, `.knowledge/plans/PLAN-008.md`, `.knowledge/plans/PLAN-009.md`

### Next steps (priority order)

1. **Push to Railway**: `git push origin main` — Railway auto-deploys via `railway.toml`. Commit `8841b84` ready.
   - Note: seed typo fix (`rr_03`) made this session — NOT yet committed. Commit before pushing.
2. **IES + UPSC dashboards**: Apply same "summary + expand" panel pattern (Must-Know, Subject Coverage, Top Gaps) — RBI done, IES/UPSC are candidates.
3. **`rbi_prep_bp.py` key data from DB**: The prep page "Key Data" tab still reads from the Python `KEY_SECTIONS` constant. Migrate to fetch from `rbi_key_data` DB table (same as dashboard).

### Open bugs (unchanged from S18)

- BUG-009: Transaction rollback silently swallows `gap_state_events` — LOW

---

## Session 18 Summary (2026-06-06)

Flask app live. Commits: `81b5600`, `1384854`, `f68b976`, `6968d5d`, `6fab62d`.
5 UI fixes (English dashboard, Begin Study→PYQ redirect, RBI data sync, diagram warning, MathJax) + 3 critical bug fixes (BUG-016 Jinja2 `.items`, BUG-017 tab panel siblings, BUG-018 drill scoring always 0).
Route count at session end: 32. Knowledge: PLAN-007 added.

---

## Session 16 Summary (2026-06-05)

---

## Session 16 Summary (2026-06-05)

### English Practice module — full implementation

**New module: `scoring/` (4 files)**
- `scoring/__init__.py` — exports `score_answer`, `build_feedback`, `RUBRICS`, `compute_self_assess_score`
- `scoring/normaliser.py` — NFKC unicode + lowercase + 40+ economics abbreviation expansion (GDP, CAD, FIT, MPC, etc.) + strip punctuation
- `scoring/keyword_scorer.py` — hybrid keyword scorer: exact + SequenceMatcher fuzzy (threshold 0.82), stuffing detection, penalty system; `score_answer()` + `build_feedback()` + grade thresholds (Excellent ≥85%, Good ≥70%, etc.)
- `scoring/self_assess.py` — `RUBRICS` dict for essay/précis/rc/letter/report + `compute_self_assess_score()`

**New page: `web/pages/11_English_Practice.py`**
- 3-phase flow: write → auto_scored → done (mirrors quiz page pattern)
- Phase 1: adaptive section labels/heights per question type, "Score My Answer →" button
- Phase 2: 4 score cards + keyword hit/miss chips + model answer expanders + rubric checkbox form
- Phase 3: side-by-side Keyword Coverage % + Structure Quality, per-section tabs, disclaimer
- Auth: `require_user(conn)` at top

**New script: `scripts/seed_english_content.py`**
- Creates 4 tables idempotently, seeds 3 question types (essay, précis, rc) and 4 initial questions
- `eng_essay_001`: CAD analysis (RBI-style, 40m, medium)
- `eng_essay_002`: FIT framework evaluation (RBI, 40m, hard)
- `eng_precis_001`: Financial inclusion passage ~420 words → model précis ~140 words (UPSC, 30m)
- `eng_rc_001`: RBI FIT accountability mechanism (RBI, 10m, easy)

**`web/app.py` — 2 changes:**
- English Practice tables created in migration block (idempotent `CREATE TABLE IF NOT EXISTS`)
- Page registered as `_english` and added to "Practice" nav section

**`.knowledge/plans/PLAN-005.md`** — English module plan; status APPROVED

### Current state at session end
- All 7 files created successfully
- DB tables exist (via app.py migration) — seed script NOT yet run (was blocked at session end)
- **Immediate next step: run seed script, then smoke-test the page**

### Next steps (priority order)
1. **Run seed**: `/opt/homebrew/bin/python3.11 scripts/seed_english_content.py`
2. **Smoke-test**: Start app, navigate to English Practice, test write → score → self-assess → results flow with `eng_essay_001`
3. **Option C content pipeline**: Create `scripts/tag_english_keywords.py` — Haiku batch for more questions at scale
4. **Rahul reviews** seeded questions and keyword tags before expanding to full batch
5. **Phase 2 question types**: Formal Letter + Report Writing (UPSC-specific, lower frequency)

---

## Session 15 Summary (2026-06-05)

### Multi-exam dashboards + plan reduction + exam date labels

**New page: `web/pages/RBI_Dashboard.py`**
- Days to 14th June countdown (orange <7d, yellow ≤14d, blue otherwise)
- Phase 1: questions answered / 267, accuracy %, total attempts
- Mastery Score (weighted avg) + Exam Readiness (gap-adjusted)
- Topics ≥50% covered metric
- Subject coverage bars (9 subjects, weighted by topic importance)
- Top gaps list sorted by flag_impact (weight × uncovered fraction)
- Quick link → RBI Prep page
- Auth: validates session against ies.db, then opens rbi.db independently

**New page: `web/pages/UPSC_Dashboard.py`**
- Days to ~22 Aug 2026 (tentative) countdown
- Auto-initialises `gap_states` in upsc.db for any new user (same schema as IES)
- Paper I (Theory) + Paper II (Indian Economy) tabs — same Begin Study/Quick Verify/Reset buttons as IES Dashboard
- Model answers coverage: 908/908 (100%) metric
- Topics Verified / In Progress / Topics Complete (%) metrics
- Overview state counts (same 6-state grid as IES)

**Dashboard.py (IES) — cross-exam hub**
- Reads `exam_focus` from users table
- If "rbi" or "upsc" in focus: shows `st.page_link` buttons at top → RBI/UPSC dashboards
- Zero disruption to existing IES content

**app.py — nav restructure**
- New "Dashboards" section: IES Dashboard (default) · RBI Dashboard · UPSC Dashboard
- IES Dashboard retains default=True (home icon)

**Study plan templates: 144 → 24**
- Dropped: `["ies","rbi"]` multi-exam subset (edge case)
- Collapsed 3 buckets → 2: crunch (≤15d) and standard (>15d). "Intensive" removed everywhere.
- Collapsed 3 prep levels → 2: `fresh` and `revision`. "Foundation" dropped.
- Collapsed 4 modes → 2: `answers_only` and `full_prep`. "mcq_drill" and "mixed" dropped.
- Changes: `scripts/generate_study_plan_templates.py`, `web/db.py`, `web/pages/8_My_Setup.py`
- **Action needed**: re-run `python scripts/generate_study_plan_templates.py` to populate new 24 templates (~$0.03, ~30s)

**Exam date labels everywhere**
- IES: "19-21 June", RBI: "14 June", UPSC: "~Aug 2026"
- UPSC Mains 2025 confirmed: Aug 22-31, 2025 (official). 2026 dates not announced; placeholder Aug 22 2026 used.
- In: My Setup checkboxes, plan template prompts, dashboard subtitles

**Commit:** `5a488af` — feat(s15): RBI+UPSC dashboards + plan reduction 144→24 + exam date labels

### Next steps (priority order before exams)

1. **Deploy S15 to Railway**: `git push origin main` → Railway auto-deploys. No schema changes needed.
2. **Re-generate study plan templates (24 new plans)**: Run `python scripts/generate_study_plan_templates.py` with `ANTHROPIC_API_KEY` set. Old 144-template table stays intact; new keys are different so no conflicts — but old keys (intensive/foundation/mixed buckets) won't be matched anymore. Either: (a) clear the table first (`DELETE FROM study_plan_templates`), or (b) leave it and let old users fall through to AI generation.
3. **Feedback system** (BUG-007 + new feature): Next big feature. Schema designed in PLAN-002. Needs GitHub personal access token with `issues:write`.
4. **Fix BUG-010** before multi-user scale: `set_topic_state()` uses internal `get_user_id()` — wrong-user write risk. Pass `user_id` explicitly.

### Watch for
- UPSC Dashboard: `gap_states` for real users in upsc.db may have `user_id='rahul'` (BUG-011 fallback). If the production user's UUID is different, they'll see empty UPSC topics until they click any state button (which triggers `_init_user()`). Not a crash — just no initial state.
- English Practice page (`11_English_Practice.py`) was added in a parallel session — already in app.py nav. Not part of S15; treat as pre-existing work.

### Open bugs (unchanged from S13–S14)
- BUG-007: Connection leaks — 12+ `st.stop()` paths bypass `conn.close()`
- BUG-008: OAuth CSRF — state param not validated on callback
- BUG-009: Transaction rollback silently swallows `gap_state_events`
- BUG-010: `set_topic_state()` calls `get_user_id()` internally — wrong-user writes possible (HIGH)
- BUG-011: `"rahul"` fallback in `get_user_id()` — MEDIUM
- BUG-012: `1_Model_Answers.py` + `7_UPSC_Mains.py` unauthenticated — confirm if intentional

---

## Session 14 Summary (2026-06-05)

### 3 features shipped + 3 bugs fixed during testing

**Feature 4c — Dashboard labeling (Dashboard.py)**
- Buttons: Begin Study / Resume / Mark Partial / Mark Verified / Quick Verify / Reset
- Priority score: raw float → Top/High/Medium/Lower priority + "exam frequency + recency + gap" sub-label
- Today's Focus: state-aware context note per card ("not yet started", "needs a quick refresh" etc.)
- Overview state labels: plain English (Not Started, In Progress, Needs Refresh, Needs Work…)

**Feature 1 — Persistent login (auth.py, app.py, 0_Login.py, 10_Profile.py, init_db.py, requirements.txt)**
- "Keep me signed in for 30 days" checkbox on login page
- `remember_me` flag encoded into OAuth state param (survives Google redirect)
- `de_session` browser cookie written after callback; read on every page load via `CookieManager`
- Sign-out deletes only this device's session token (multi-device safe)
- Migration: `ALTER TABLE sessions ADD COLUMN remember_me INTEGER DEFAULT 0`
- Production: `remember_me` column confirmed live ✅

**Feature 3 — Pre-generated study plan templates (db.py, 8_My_Setup.py, init_db.py)**
- `study_plan_templates` table in schema; lookup before API call in My Setup
- `get_study_plan_template()` in db.py — silent None fallback if table absent
- `scripts/generate_study_plan_templates.py` ready to run (144 plans, ~$0.15)

**3 bugs fixed during testing:**
- BUG: `CookieManager(key="main")` instantiated 3x → `StreamlitDuplicateElementKey` — fixed by singleton in app.py shared via `st.session_state["_cookie_mgr"]`
- BUG: `validate_session` crashed on naive datetimes from SQLite default — fixed by adding UTC tzinfo when absent
- BUG: "Page not found" flash after cookie restore — fixed by `st.rerun()` after session bootstrap

**Commits this session:**
- `da52e12` — feat(s14): persistent login + plan templates + dashboard labeling
- `ba83b9b` — fix(auth): cookie duplicate key + datetime tz + rerun on restore

**Deployed:** `ies-descriptive-prep-production.up.railway.app` — deployment `1891c838` ✅

### Next steps
1. **Manual test "Remember me"**: Go to production, check the box, sign in with Google, close browser, reopen — should auto-sign back in without login page
2. **Generate plan templates**: `python scripts/generate_study_plan_templates.py` (~$0.15, ~3 min, needs `ANTHROPIC_API_KEY`)
3. **Feature 2 (Feedback system + GitHub Issues)**: Schema designed, ready to build. Needs GitHub personal access token with `issues:write` scope
4. **Feature 4 (Dynamic dashboard)**: Phase 1 (IES↔UPSC switching) and Phase 2 (RBI, different schema) planned

### Open bugs (unchanged from S13)
- BUG-007: Connection leaks — 12+ `st.stop()` paths bypass `conn.close()`
- BUG-008: OAuth CSRF — state param carries `remember_me` flag but CSRF token not validated on callback
- BUG-009: Transaction rollback silently swallows `gap_state_events`
- BUG-010: `set_topic_state()` calls `get_user_id()` internally — wrong-user writes possible
- BUG-011: `"rahul"` fallback in `get_user_id()` — MEDIUM
- BUG-012: `1_Model_Answers.py` + `7_UPSC_Mains.py` unauthenticated — confirm if intentional

---

## Session 13 Summary (2026-06-05)

### Production crash fix + full architectural audit

**Production crash (reported live):**
- `ies-descriptive-prep-production.up.railway.app` showed "Page not found: pages/Dashboard.py" after Google OAuth
- Root cause: NAV-001 pattern — `st.switch_page()` to a page not in the current `st.navigation()` registration
- Fix: replaced with `st.rerun()` in `0_Login.py` (commit `0fec71e`)

**Full architectural audit (3 parallel agents):**
- Audit scope: auth/navigation flow, multi-user data isolation, quiz submission + DB connections
- 12 bugs found total: 6 fixed this session, 6 remain open

**Bugs fixed (commit `831479c`):**
- BUG-002: Logout crash (same NAV-001 pattern, Profile.py:189)
- BUG-003: `require_user()` nav mismatch + connection leak (auth.py:135)
- BUG-004: Session state bleed between users (quiz_, rq_, rbi6_ keys not cleared on login)
- BUG-005: `attempt_count` race condition — replaced Python read-modify-write with SQL `attempt_count+1`
- BUG-006: Quiz accepted partial answers — `any()` → `all()` for intro/body/conclusion validation

**Bugs still open (see .knowledge/INDEX.md):**
- BUG-007: Connection leaks from st.stop() (12+ paths) — needs try/finally refactor
- BUG-008: OAuth CSRF — state param not validated — LOW, pre-public-launch
- BUG-009: Transaction rollback silently swallows gap_state_events — LOW
- BUG-010: set_topic_state() uses get_user_id() internally — HIGH, fix before multi-device
- BUG-011: "rahul" fallback in get_user_id() — MEDIUM
- BUG-012: 1_Model_Answers.py + 7_UPSC_Mains.py unauthenticated — confirm if intentional

**Knowledge base system bootstrapped (commit `007111f`):**
- `.knowledge/` directory: 12 bug records, 1 audit record, 1 plan, 1 diagnostic
- `CLAUDE.md` created with read/write contract
- Stop hook added to `.claude/settings.json`
- Global patterns at `~/.claude/knowledge/patterns/`: NAV-001, SESSION-001, DB-001
- Same system applied to Devthorium project

### Commits this session
- `0fec71e` — fix(auth): OAuth callback nav crash
- `831479c` — fix(audit): 5 architectural bugs from S13 audit
- `007111f` — chore(knowledge): bootstrap .knowledge/ system + CLAUDE.md

### Next steps (post-exam June 21+)
1. Fix BUG-007 (connection leaks) — try/finally refactor across all pages
2. Fix BUG-010 (set_topic_state explicit user_id param)
3. Build payment wallet per `docs/PAYMENT_PLAN.md`
   - Razorpay KYC must be started NOW (razorpay.com — 1–3 day external wait)
   - Build order: DB migrations → billing.py → webhook.py → Wallet page → Quiz gate → Answer Review

---

---

## Session 12 Summary (2026-06-04)

### YouTube playlists + Railway migration

**YouTube playlist cleanup**
- IES playlist `PLG8cSH86vt8YyNB-tJPdFkp59B33ZFoRj` — was 23/24. Found missing video GE-03 A2b (`-gp9eYZKN_o`). Now 24/24 ✅
- RBI DEPR playlist created: `PLG8cSH86vt8b8JDlHZMxMS5c0pIuLn-Li` — all 6 episodes added (A1→A6 order) ✅
- `web/resources.py` — IES and RBI `url` fields updated from channel root to specific playlist URLs ✅

**Railway data migration — RBI mastery**
- Designed `scripts/migrate_mastery_to_railway.py`: hardcodes 29 mastery rows + 7 attempt rows from local export
- Generated SSH key (`~/.ssh/id_ed25519`) and registered with Railway (`railway ssh keys add`)
- Added Railway host key to `~/.ssh/known_hosts` via `ssh-keyscan ssh.railway.com`
- Committed + pushed → Railway redeployed (deployment `15db2dda`, SUCCESS)
- Ran `railway ssh python scripts/migrate_mastery_to_railway.py` — non-interactive SSH command
- Result: 29 mastery rows + 7 attempts migrated to Railway `rbi.db` under UUID `cb618995-ae85-43eb-91b3-e19474acd1b7` ✅

**Key architectural clarification discovered:**
- `railway run` = LOCAL command with Railway env vars injected. Does NOT access Railway volume files.
- `railway ssh [COMMAND]` = runs inside the container. Required for any script that touches `/app/data/*.db`.
- SSH key must be generated locally + registered via `railway ssh keys add` before first `railway ssh` use.

**Commits this session:**
- `0f52dd3` — migration script + real playlist URLs in resources.py

### Exact next steps

**Remaining pre-exam (before June 14 RBI / June 19 IES):**
1. Start Razorpay KYC now (razorpay.com — 1–3 day external wait, no code needed)
2. Drill on Railway app daily: RBI Phase 1 → IS-LM first (flag_impact 0.20)

**Post-exam (June 21+):**
3. Build payment wallet per `docs/PAYMENT_PLAN.md` (~23h, 8–9 days at 2–4h/day)
   - Critical path: Razorpay KYC must be done BEFORE starting Step 3
   - Build order: DB migrations → billing.py → webhook.py → Wallet page → Quiz gate → Answer Review

---

## Session 11 Summary (2026-06-04)

### Railway deploy + UX fixes

**Railway deploy — LIVE ✅**
- App live at `https://ies-descriptive-prep-production.up.railway.app`
- Volume mounted at `/app/data` (persistent across redeploys)
- Google OAuth working (redirect URI fixed: `/Login` not `/0_Login`)
- All 4 env vars set: `ANTHROPIC_API_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_REDIRECT_URI`
- Seed DB fix: moved `seeds/` outside `data/` so Railway volume mount doesn't hide them

**Navigation redesign (st.navigation)**
- `app.py` rewritten as pure router using `st.navigation()` — auth-aware sections
- Dashboard content moved to `web/pages/Dashboard.py`
- Logged-out: sidebar shows only "Sign In"
- Logged-in sidebar: Dashboard + Study (IES PYQs, Study Brief, UPSC Mains) + Practice (Quiz, Return Quiz, RBI Prep) + Progress (My Progress, Answer Review) + Account (My Setup, Profile)
- "app" and "Login" clutter gone; Login never shows when authenticated

**Single-session enforcement**
- `auth.py` `create_session()` now deletes ALL prior sessions before creating new one
- One active login per account at all times

**Profile page (`web/pages/10_Profile.py`)**
- Avatar, display name, email, member since, subscription tier badge
- Phone number field (optional, editable)
- Study snapshot: answers graded, MCQs attempted, exam focus + date
- Sign Out button (clears all sessions + session state)

**Quiz — Coming Soon gate**
- Quiz loads fully (question, rubric, answer boxes)
- Submit button disabled + `🔒 AI grading coming soon · ₹4.50 per answer` pill below it
- Users see exactly what they're paying for before committing

**Resource URL fix**
- `8_My_Setup.py` AI plan no longer generates URLs — `_authoritative_resources()` always injects from `resources.py` after generation
- Prevents hallucinated `/c/MrunalPatel` YouTube URLs and broken internal app links

**IES PYQs rename**
- `1_Model_Answers.py` page title + heading updated to "IES PYQs — Model Answers"

**Payment plan**
- Full plan saved to `docs/PAYMENT_PLAN.md`
- Razorpay wallet, ₹4.50/answer, ₹100–₹2000 top-ups, atomic deduction, 7-day grace
- ~23h build estimate, post-exam (after June 21)
- Start Razorpay KYC now (1–3 day external wait)

**Railway CLI installed**
- `railway` CLI at `/opt/homebrew/bin/railway` v4.66.2

**Commits this session:**
- `70da9a3` — seeds/ dir fix (volume mount issue)
- `f89c916` — resource URL fix (AI hallucination prevention)
- `f823c31` — Coming Soon gate + payment plan doc
- `1009de5` — locked submit button with teaser
- `c050ab9` — nav redesign + profile + single-session + rename

### Exact next steps

**Rahul must do:**
1. **Data migration** — after confirming sign-in on Railway works:
   ```bash
   railway link   # select melodious-surprise → production
   railway run python scripts/migrate_local_data.py
   ```
   This links your local RBI mastery data (29 rows) to your Google account UUID.

2. **Start Razorpay KYC** (takes 1–3 days, external) — go to razorpay.com, sign up with PAN + bank account. Build the payment wallet while KYC is processing.

3. **Add YouTube playlist URLs** to `web/resources.py` as you upload more content to @rahuldev0108.

**After exams (June 21+):**
4. Build payment wallet feature per `docs/PAYMENT_PLAN.md` — 23h, ~9 days at 2–4h/day.
5. Implement Answer Review actual feature (behind Pro gate).

---

## Session 10 Summary (2026-06-04)

### Public-launch readiness (first half)

**Seed DBs committed (blocking deploy issue fixed)**
- `data/rbi_seed.db` created (303 questions, 0 user rows) + committed
- `data/upsc_seed.db` created (908 model answers, 0 user rows) + committed
- `app.py` first-boot logic generalised to handle all 3 DBs via `_boot_db(name)`
- `7_UPSC_Mains.py` now has explicit DB-not-found error with `st.stop()`

**Composite indexes applied**
- 6 indexes added to `ies_seed.db` + `scripts/init_db.py`
- `idx_rbi_sess_user` added to `rbi_seed.db` + `scripts/rbi/00_init_rbi_db.py`

**Deploy docs + config**
- `.env.example` updated with all 3 OAuth env vars
- `DEPLOY.md` fully rewritten: Railway step-by-step, volume mount, OAuth setup, smoke test
- `.gitignore` simplified to `*.db-shm / *.db-wal` glob

**Smoke test:** 7/8 PASS (RBI/tabs timeout is pre-existing test-script timing issue, not a bug)

### Onboarding + personalisation (second half)

**My Setup wizard (`web/pages/8_My_Setup.py`)**
- 4 questions: exams / exam date / prep level / study mode
- AI-generated study plan via `claude-haiku-4-5` (1 call per user per onboarding)
- Rule-based fallback if `ANTHROPIC_API_KEY` not set
- Plan stored in `users.study_path` (JSON); re-accessible + updatable any time
- Shows: phase name, key insight, phase breakdown, resources, today's action, AI tip

**Dashboard `Your Path` banner (app.py)**
- Fires immediately after auth on first-time users → redirects to `8_My_Setup.py`
- After onboarding: shows current phase + today's action + "Update plan" link inline

**Page timer tracker**
- `track_page_time(conn, page_name)` in `web/db.py` — logs `page_time` events
- Wired to all 9 pages (1-liner after auth on each)
- `My Progress` page: "Today's Time" + "Last 7 Days" inline bar charts (no matplotlib)

**Answer Review stub (`web/pages/9_Answer_Review.py`)**
- Subscription-locked: `users.subscription_tier = 'free'` for all users
- Shows locked Pro card with manual workaround tip
- Actual AI feedback feature deferred; unlocks when `subscription_tier = 'pro'`

**DB changes**
- 7 new columns on `users` table: `exam_focus`, `exam_date`, `prep_level`, `study_mode`, `study_path`, `onboarding_completed`, `subscription_tier`
- Migrated `ies.db` (local) + `ies_seed.db` (committed) + `scripts/init_db.py`

**Supporting files**
- `web/resources.py` — configurable YouTube + AI tool resources per exam; pass-through for AI prompt
- `railway.toml` — Nixpacks builder, Streamlit start command, restart policy

**GitHub:** All commits pushed to `rahuldev3160/ies-descriptive-prep`
- `b8d4208` — seed DBs + composite indexes + deploy docs
- `dd31e39` — onboarding + timer + Answer Review
- `cfe99b8` — Railway config

### Exact next steps

**Rahul must do (requires credentials):**
1. railway.app → New Project → Deploy from GitHub → `ies-descriptive-prep`
2. Railway → Storage → Add Volume → Mount Path: `/app/data` (CRITICAL — without this DB data resets)
3. Google Cloud Console → OAuth 2.0 Client ID → get `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`
4. Railway → Variables → set all 4 env vars (see `DEPLOY.md`)
5. First deploy auto-triggers; visit the Railway URL to verify onboarding flow

**After deploy:**
- Update `web/resources.py` with specific YouTube playlist URLs as you upload more to @rahuldev0108
- Test with 2 separate Google accounts to verify user isolation

**Future features (deferred):**
- Answer Review (AI feedback on written answers) — behind Pro subscription gate
- Subscription system (payments, tier upgrades)
- Subtopic-level gap surfacing on dashboard

---

## Watch For — Active Gotchas (read before writing any code)

| Gotcha | Symptom | Correct action |
|---|---|---|
| **Wrong Python runtime** | `TypeError: unsupported operand type(s) for \|` on any page | Do NOT remove the annotation. Run `/opt/homebrew/bin/streamlit --version` to confirm runtime is Python 3.11. Never use `/Library/Python/3.9/bin/streamlit`. |
| **ies_seed.db must stay clean** | New users get Rahul's personal data on first boot | `data/ies_seed.db` is the committed clean copy — never run quiz/drill sessions against it. It must only contain question bank rows (zero user_mastery / gap_states / attempts). |
| **OAuth env vars required on deploy** | Login page shows config error; app redirects to login loop | Set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_REDIRECT_URI` on the server. App degrades gracefully without them (shows config message), but no user can log in. |

---

## Project Status

### IES 2026 — COMPLETE
Backend: 1219 PYQs + rubrics + model answers + 150 MCQs. Web app live on :8501.

### UPSC Economics Optional — COMPLETE ✅
908/908 PYQs + rubrics + model answers in `data/upsc.db`. Web app live: `web/pages/7_UPSC_Mains.py` (Paper I Theory / Paper II Indian Economy, year navigation, LaTeX rendering, rubric + data tabs).

### RBI DEPR 2026 — MCQ BANK BUILT ✅ | UI rebuilt ✅
New `data/rbi.db` with 303 questions. `6_RBI_Prep.py` fully rewritten. See below.

---

## Session 9 Summary (2026-06-03)

### Public launch preparation

**DB foundation (data layer)**
- `data/ies.db` removed from git tracking — it's the live runtime DB, not source code
- `data/ies_seed.db` created: clean copy of ies.db with all user rows stripped (12.7 MB committed)
- Both DBs have `user_events` table + 2 indexes (`idx_ue_user`, `idx_ue_type`)
- First-boot logic in `app.py`: if `ies.db` missing → copy from `ies_seed.db` (with error handling)

**User isolation fixes**
- `6_RBI_Prep.py` hardcoded `USER_ID = "rahul"` → `get_user_id()` (6 call sites)
- `4_My_Progress.py` direct `USER_ID` import → `get_user_id`
- `get_user_id()` in `db.py` now auto-assigns UUID on first call from ANY page (deep-link safe — no more "rahul" fallback)

**Event logging**
- `log_event()` added to `web/db.py` — silent no-op on any error
- `session_id` falls back to `user_id` (since they're the same in pre-auth architecture)
- Wired: `topic_opened` (Study Brief), `return_quiz_submitted` (Return Quiz), `drill_attempt` (RBI Prep)

**Public-safe API**
- `2_Quiz.py` gated: if `ANTHROPIC_API_KEY` not set → info banner + st.stop()
- `load_api_key()` dev machine path removed (hard raise only)
- `playwright` removed from `requirements.txt` (5 prod deps remain)

**Config / infra**
- `.gitignore`: `data/ies.db`, `data/rbi.db`, all WAL files for all 3 DBs
- `DEPLOY.md`: Python 3.11, Hetzner/Railway targets, quiz API key note
- `scripts/init_db.py`: `user_events` table added to schema

### Also completed this session (auth + connections)

**Google OAuth auth layer**
- `web/auth.py`: full OAuth helper library — `build_auth_url`, `exchange_code`, `get_user_info`, `upsert_user`, `create_session`, `validate_session`, `require_user`
- `web/pages/0_Login.py`: login page; handles callback (`?code=`) + sign-in button; degrades gracefully if OAuth env vars absent
- `users` + `sessions` tables in schema + both DBs migrated
- `require_user()` gating: `app.py`, `2_Quiz.py`, `3_Study_Brief.py`, `4_My_Progress.py`, `5_Return_Quiz.py`, `6_RBI_Prep.py` (ies auth conn → close → rbi page conn)
- `1_Model_Answers.py` and `7_UPSC_Mains.py` intentionally open (read-only public pages)

**Per-request DB connections (DECIDE-08)**
- All 7 pages migrated from `@st.cache_resource _get_conn()` to per-request `conn = get_conn()` + `conn.close()` at end
- `get_conn()` now sets `PRAGMA journal_mode=WAL` + `PRAGMA busy_timeout=5000` on every connection
- `6_RBI_Prep.py` and `7_UPSC_Mains.py` inline connections also get WAL pragmas

**Commits:** `ac1ad73` (seed DB + standalone fixes) → `ae3e409` (auth + connections)

### Remaining before public launch (1 item)

- **Composite indexes** (7 indexes, 15 min) — SQL already written in `memory/project_multiuser_plan.md`. Needed at >100 users. Not urgent for first launch.

### Layered-coverage gap noted (future work)
The dashboard shows topic-level gap states but does not surface subtopic-level gaps. A topic at "20% mastered" can hide 5 completely untouched subtopics. The `at_risk_children` concept from the layered-coverage framework should be added to the dashboard post-launch.

---

## Session 8 Summary (2026-06-03)

### What was done this session

**1. matplotlib installed — Model Answers page unblocked**

`ModuleNotFoundError: No module named 'matplotlib'` on `1_Model_Answers.py:8`. Root cause: matplotlib was installed in system Python 3.9 but Streamlit runs on Homebrew Python 3.11. Fixed by installing into the correct interpreter:
```bash
/opt/homebrew/opt/python@3.11/bin/python3.11 -m pip install matplotlib numpy
```

**2. All Critical + High IES bugs fixed**

| Bug | File | Fix |
|---|---|---|
| Connection leak (CRITICAL) | All 5 IES pages | `@st.cache_resource` on `_get_conn()` in each page; removed all `conn.close()` calls |
| Silent DB save failure (CRITICAL) | `2_Quiz.py:532` | `except: pass` → `st.toast(f"Could not save attempt: {err}", icon="⚠️")` |
| Mastery not written on first attempt (HIGH) | `db.py` `submit_return_quiz` | Added `INSERT OR IGNORE INTO user_mastery` before `UPDATE` — ensures row always exists |
| No transaction in `submit_return_quiz` (HIGH) | `db.py` | Refactored: all reads moved before writes, all writes wrapped in `with conn:` atomic block |
| FD leak in `@st.cache_data` (HIGH) | `2_Quiz.py:92` | Added `try/finally c.close()` in `_load_all_questions` |
| Option sort scramble (MEDIUM) | `5_Return_Quiz.py:149,204` | `key=lambda x: x[0]` → `sorted()` on full string |

**3. Smoke test: 11/11 PASS** (up from 10/11 last session — Model Answers now fixed)

**4. Multi-user architecture planned (parallel agents)**

Full plan in `memory/project_multiuser_plan.md`. Key outputs:
- 16 DECIDE items, 9 ASSUME items, scale failure sequence
- MVMU = 6 changes, 5–7 focused days, safe to launch after that
- Discovered RISK-02: `6_RBI_Prep.py:21` `USER_ID = "rahul"` is a live bug even now
- Discovered DECIDE-08: `@st.cache_resource` is correct for single-user but wrong for multi-user

**5. UPSC Mains model answers page built** (`web/pages/7_UPSC_Mains.py`)

Standalone page querying `data/upsc.db` directly (exam_id=`upsc_eco_opt`). Sidebar: Paper I (31 topics, 477 Qs) / Paper II (50 topics, 431 Qs). Year radio navigation, LaTeX renders via `st.markdown()` KaTeX, rubric + data tabs. `@st.cache_resource` connection (no leak). Verified live: 11/12 PASS.

**6. Python 3.11 upgrade — permanent fix (root cause analysis)**

Root cause: project was split across Python 3.9 (Streamlit, broken pip) and Python 3.11 (Homebrew, already fully installed). `X | Y` union syntax appeared first in batch scripts (no crash), then crashed when it hit a Streamlit page. The `project_ies_exam_prep.md` memory file actively propagated the wrong 3.9 path to every session. Three structural fixes applied:

| Fix | What changed |
|---|---|
| Runtime | `streamlit run` now uses `/opt/homebrew/bin/streamlit` (Python 3.11) everywhere |
| Lock files | `.python-version` (3.11), `requirements.txt` (pillow + playwright added) |
| Memory | `project_ies_exam_prep.md` corrected 3.9→3.11; `feedback_python_version.md` created |
| run-app skill | Error triage block added — classify error before touching code |
| HANDOFF.md | `Watch For` section added at top |
| dev-workflow skill | L-DEV-29 (pin runtime at day zero), L-DEV-30 (classify before fixing), Error Triage Protocol section |

---

## Session 7 Summary (2026-06-03)

### What was done this session

**1. RBI Prep — 5 bugs fixed in `web/pages/6_RBI_Prep.py`**

| Bug | Root Cause | Fix |
|---|---|---|
| `KeyError: 'attempts'` crash on My Progress tab | `get_progress_data()` SELECT at line 156 listed 6 columns but excluded `attempts`; line 194 accessed `m["attempts"]` | Added `attempts` to SELECT |
| Phase 1 Drill explanations only shown for wrong answers; capped at 200 chars | `if not r["is_correct"]:` guard on explanation render; `[:200]` truncation | Removed guard, removed truncation |
| Phase 1 results view: single flat expander for all questions | Used one `st.expander("View breakdown")` containing plain text per question | Replaced with per-question expanders (Tier 2 style): option highlighting + full `Why:` for every question |
| Vague score card label `X% — Session complete` | Hardcoded copy | Changed to `Phase 1 Drill — X% correct` |
| Progress tab jargon labels `Formula Readiness` / `True Readiness` | Not self-explanatory to user | Changed to `Mastery Score (weighted avg)` / `Exam Readiness (gap-adjusted)` |

**2. Tier 2 Quiz — expanded from 36 to 54 questions (6 → 9 buckets)**

Three new buckets added to `BUCKETS` dict in `6_RBI_Prep.py`:

| Bucket | Key topics |
|---|---|
| 🌐 External Sector & BoP | BoP structure, CAD drivers, REER vs NEER, forex reserves, FDI vs FPI, ECB |
| 🏢 NBFC & Regulatory Framework | NBFC vs bank, SBR Upper Layer, HFC transfer to RBI (2019), P2P, Account Aggregator, NOF |
| 🏛 International Finance & Institutions | BIS/Basel, SDR basket, World Bank IDA vs IBRD, FSB, NDB (Shanghai), IMF conditionality |

Sufficiency analysis: 54 is the stopping point. Capital Markets and Agricultural Finance (NABARD) are low-weight in Phase 1 MCQ; better addressed in Phase 2 descriptive prep. Phase 1 DB (267 Qs) covers the theory gap.

**3. Streamlit testing — solved for entire model**

Root cause: Streamlit's React layer CSS-hides native `<input type="radio">` and custom-renders dropdowns. Native Playwright locators fail silently.

- Created `scripts/streamlit_test_utils.py` — reusable helpers for all pages: `answer_radio_groups()`, `click_tab()`, `submit_form()`, `check_for_errors()`, `run_smoke_test()`
- Created `.claude/skills/run-app/SKILL.md` — project skill documenting server start, all 7 pages, Playwright patterns, known IES bugs
- Confirmed working: `python3 scripts/streamlit_test_utils.py` runs smoke test across all 7 pages (10/11 PASS; Model Answers fails on pre-existing db.py:44 bug)

**4. All changes verified live**

Smoke test results:
```
✅ app, Quiz, Study Brief, My Progress, Return Quiz, RBI Prep
✅ RBI/Key Data, RBI/Phase 1 Drill, RBI/Tier 2 Quiz, RBI/My Progress
❌ Model Answers — pre-existing db.py:44 connection bug (not this session)
```

**5. Memory + skills updated**
- `memory/project_ies_exam_prep.md` — session 7 patch notes, Tier 2 count updated
- `memory/feedback_streamlit_testing.md` — NEW: full Playwright patterns for Streamlit
- `memory/MEMORY.md` — index updated
- `SKILL_REGISTRY.md` — run-app skill added
- `development-workflow` skill — L-DEV-28 added (Streamlit testing pattern)

---

## Exact Next Steps (from Session 8 / Python upgrade session)

### STUDY (before June 14 RBI exam — 11 days):
All bugs fixed. App is 12/12 pages working. Python 3.11 canonical. **Use the app.**
- RBI Phase 1 Drill → Smart Serve daily (IS-LM first, highest flag_impact = 0.20)
- UPSC Model Answers → review by topic (Paper I theory, Paper II Indian Economy)
- Return Quiz for IES topic verification
- Mundell-Fleming top-up: `scripts/rbi/06_topup_questions.py` — only 7 Qs, need ~13 more (not yet built)

### MVMU — MINIMUM VIABLE MULTI-USER (post-exam, 5–7 days, do in order):

Full plan: `memory/project_multiuser_plan.md` — 16 DECIDE items.

**Step 1 — Fix live RBI data corruption (30 min) ← DO FIRST**
`6_RBI_Prep.py:21`: `USER_ID = "rahul"` hardcoded. All RBI attempts from any user save as "rahul".
Fix: replace with `get_user_id()` from `db.py`.

**Step 2 — Revert @st.cache_resource → per-request connections (1 hour)**
All 5 IES pages currently use `@st.cache_resource` for DB connections — correct for single-user,
wrong for multi-user (Python sqlite3 not thread-safe at connection-object level). Replace with:
```python
conn = get_conn()
try:
    # page logic
finally:
    conn.close()
```
Also enable WAL mode in `get_conn()`: `conn.execute("PRAGMA journal_mode=WAL"); conn.execute("PRAGMA busy_timeout=5000")`

**Step 3 — Add users + sessions tables + Google OAuth (2–3 days)**
- `migrations/002_add_users_sessions.py` — schema from `memory/project_multiuser_plan.md`
- `pages/0_Login.py` — Google OAuth via `authlib`
- `web/auth.py` — `require_user()`, `validate_session_cookie()`, `create_session()`

**Step 4 — Auth gate on every page (half day)**
Replace `conn = get_conn()` at top of every page with `uid = require_user()` (hard-stops to login if unauthenticated). Remove fallback-to-"rahul" from `get_user_id()`.

**Step 5 — Rate limiting (half day)**
Add `daily_api_calls` + `quota_resets_at` to `users` table. Implement `check_and_increment_quota()` in `db.py`. Wire into `2_Quiz.py` before every AI call. Limit: 20 calls/day ($1.80/user/month max).

**Step 6 — Remove .env fallback from load_api_key() (15 min)**
Delete the path fallback in `db.py:83`. Hard `raise ValueError` if `ANTHROPIC_API_KEY` env var not set.

**Step 7 — Add composite indexes (15 min)**
```sql
CREATE INDEX idx_da_user_exam     ON descriptive_attempts(user_id, exam_id, created_at DESC);
CREATE INDEX idx_gse_user_topic   ON gap_state_events(user_id, topic_id, exam_id, created_at DESC);
CREATE INDEX idx_rqa_user_topic   ON return_quiz_attempts(user_id, topic_id, exam_id, created_at DESC);
CREATE INDEX idx_um_user_exam     ON user_mastery(user_id, exam_id);
CREATE INDEX idx_gs_user_exam_st  ON gap_states(user_id, exam_id, state);
CREATE INDEX idx_tas_user_exam    ON topic_attempt_summary(user_id, exam_id);
```

**Step 8 — Deploy on Hetzner CX21 (~€4.5/mo) or Railway ($5/mo)**
Single-process Streamlit + SQLite WAL. Set `ANTHROPIC_API_KEY` + Google OAuth credentials as env vars. Enable HTTPS (Caddy). Smoke test with 2 separate Google accounts.

### DEFERRED (after exams + MVMU):
- UPSC Mains web tab (`7_UPSC_Mains.py` + `8_UPSC_Model_Answers.py`)
- `user_events` universal audit log (DECIDE-15)
- `schema_versions` migration tracking (DECIDE-16)
- Migrate to PostgreSQL at 500 users (DECIDE-14)

---

## Session 6 Summary (2026-06-03)

### What was done this session

**1. Full project audit (parallel subagents)**

Code review subagent identified 13 bugs across `web/` pages:
- 2 CRITICAL: DB connection leak (OperationalError on concurrent sessions), silent quiz save failure
- 6 HIGH: wrong user data on direct page open, FD leak in cache, no transaction in submit_return_quiz, mastery never written on first attempt, rate-limit state initialized too late, duplicate questions from LEFT JOINs
- 3 MEDIUM: hardcoded dev path in API key loader, data contradiction in ie_3 (2011-12 vs 2022-23), option sort scrambling
- 2 LOW: dead code, legacy schema blank scores

**NOTE:** IES tab bugs (2_Quiz.py, 5_Return_Quiz.py, db.py) are NOT fixed yet. Fix them before the IES exam (June 19).

RBI analysis subagent confirmed:
- `6_RBI_Prep.py` was hardcoded (no DB, no AI), session-state only (scores lost on refresh)
- Phase 2 quiz wrapped silently to bucket 0 on completion — no handler
- ZERO RBI content in `ies.db` — no `rbi_` tables anywhere
- Phase 1 (70% of prep = 17 Tier 1 theory topics) was entirely missing

**2. Architecture decision: Stay in this app (not Devthorium)**
Devthorium = UPSC prelims MCQ tool, wrong fit for RBI descriptive prep.

**3. RBI MCQ bank — fully built**

| Script | Result |
|---|---|
| `scripts/rbi/00_init_rbi_db.py` | 5-table schema: rbi_questions, rbi_attempts, rbi_topic_mastery, rbi_sessions, rbi_topic_weights |
| `scripts/rbi/01_seed_topic_weights.py` | 29 topic weights from 2024 actual paper distribution |
| `scripts/rbi/02_generate_mcq_bank.py` | Haiku batch → 230 inserted, 5 failed (LaTeX) |
| `scripts/rbi/03_migrate_tier2.py` | 36 existing hardcoded Tier 2 questions → DB |
| `scripts/rbi/04_compute_weights.py` | priority_weight, flag_impact computed per question/topic |
| `scripts/rbi/05_fix_parse_errors.py` | Per-object JSON extraction fix for 5 failed topics → +73 questions |

**Final DB state:**
```
rbi_questions:     303 total (267 Tier 1 theory + 36 Tier 2 current affairs)
rbi_topic_weights: 29 topics with 2024 paper-derived weights
rbi_topic_mastery: 24 topics (seeded for user 'rahul')
rbi_attempts:      0 (fresh start)
Trap questions:    114 (38%)
Hard questions:    87 (29%)
```

**Priority order (flag_impact):**
1. is_lm (0.20) — Macro, 16 questions
2. mundell_fleming (0.10) — Intl Econ, 7 questions (17 from fix + more batching needed)
3. india_macro_data (0.09) — Indian Economy, 21 questions
4. qtm_monetary (0.08) — Macro, 15 questions
5. classical_growth (0.07) — Growth, 15 questions

**4. `6_RBI_Prep.py` fully rewritten (4 tabs)**

| Tab | Status | What it does |
|---|---|---|
| 📊 Key Data Cards | ✅ unchanged | 6 sections, ~35 verified data items |
| 🧠 Phase 1 Drill | ✅ NEW | Smart Serve (coverage-driven) + Filter mode, reads from rbi.db, saves attempts, updates mastery with INSERT OR REPLACE |
| ❓ Tier 2 Quiz | ✅ fixed | 6 buckets, completion bug FIXED, aggregate summary on all-done, weakest-bucket CTA |
| 📈 My Progress | ✅ NEW | Formula readiness + True readiness, gap alerts sorted by flag_impact, subject coverage bars |

**All IES code review mistakes avoided in new RBI UI:**
- `@st.cache_resource` connection (no leak)
- `with conn:` transaction in save_attempt
- `INSERT OR REPLACE` for mastery (no first-attempt miss)
- `USER_ID = "rahul"` constant (no session state dependency)
- All session state in `_SS_DEFAULTS` dict at top of file
- `st.toast()` on DB error (no silent failure)
- ie_3 corrected: base year → 2022-23 (was 2011-12 — was wrong)

**5. Web research (subagent)**
ixamBee 2024 PYQ analysis confirmed: International Economics is rank 2 (10-11 questions), not rank 4. Mundell-Fleming appeared TWICE in 2024 — now correctly weighted. 2025 paper changed to 43 questions/66 marks.

---

## Exact Next Steps

### IMMEDIATE (before June 14 exam):

**Step 1 — Mondell-Fleming question gap (needs more questions)**
Mundell-Fleming is rank 2 priority but only has 7 questions in DB (17 were generated, 10 were lost to parse errors that could only recover 7 via regex extraction). Need ~13 more.
```bash
# Re-run just mundell_fleming with direct API (not batch) to top up to 20:
# Add a one-off script: scripts/rbi/06_topup_questions.py
# Use client.messages.create() directly for intl_econ__mundell_fleming
```

**Step 2 — Fix critical bugs in IES tabs (before June 19)**
From code review — these affect data integrity NOW:
```
web/db.py:44         → @st.cache_resource connection (CRITICAL)
web/pages/2_Quiz.py:532 → except: pass on DB insert (CRITICAL)
web/db.py:469        → mastery not written on first attempt (HIGH)
web/db.py:387        → no transaction in submit_return_quiz (HIGH)
web/pages/2_Quiz.py:92  → FD leak in @st.cache_data (HIGH)
```

**Step 3 — Run the app and verify Phase 1 Drill**
```bash
/Users/rahulsingh/Library/Python/3.9/bin/streamlit run web/app.py
```
Navigate to RBI Prep → Phase 1 Drill → Start Smart Session (10 Questions)
Should show IS-LM questions first (highest flag_impact = 0.20).

**Step 4 — English paper (separate build, post-exam or quick MVP)**
Study plan has full English prep plan in `data/rbi_ies_study_plan.md:130-145`.
Build as a shared module across IES/UPSC/RBI (not RBI-specific).

### DEFERRED (after June 14):

**Step 5 — UPSC Mains web tab**
- `web/pages/7_UPSC_Mains.py` — landing dashboard
- `web/pages/8_UPSC_Model_Answers.py` — mirrors 1_Model_Answers.py but uses `data/upsc.db`
- Add multi-exam support in `web/db.py`

**Step 6 — Streamlit Cloud deploy**
Push to GitHub + set `ANTHROPIC_API_KEY` secret on share.streamlit.io.

---

## Architecture Decisions Made This Session

| ID | Decision | Rationale |
|---|---|---|
| DECIDE-06 | Separate `rbi.db`, not shared with `ies.db` | Consistent with DECIDE-01 isolation principle |
| DECIDE-07 | @st.cache_resource for DB connection in RBI pages | Fixes CRITICAL connection leak from code review |
| DECIDE-08 | INSERT OR REPLACE for mastery rows (not IF NOT EXISTS) | Fixes HIGH bug: first attempt never wrote mastery |
| DECIDE-09 | Stay in Descriptive Exams app for RBI (not Devthorium) | Devthorium = MCQ-only UPSC prelims. Wrong fit. Post-June 14: consider productising for other aspirants |
| DECIDE-10 | Priority weights derived from 2024 actual paper distribution | ixamBee PYQ analysis gave real question counts; more reliable than syllabus estimation |
| DECIDE-11 | Batch + fix script pattern (same as UPSC pipeline) | LaTeX/newlines in JSON require per-object extraction fallback; reuse existing fix_parse_errors pattern |
| DECIDE-12 | English paper as shared module across IES/UPSC/RBI | Essay appears in all three exams; don't build 3 separate implementations |

---

## File Locations

| Resource | Path |
|---|---|
| RBI DB | `data/rbi.db` |
| RBI scripts | `scripts/rbi/00_*.py` through `05_*.py` |
| RBI prep page | `web/pages/6_RBI_Prep.py` |
| IES DB | `data/ies.db` |
| UPSC DB | `data/upsc.db` |
| Study plan | `data/rbi_ies_study_plan.md` |
| NotebookLM sources | `data/notebooklm/` |
| Theory source | `data/notebooklm/rbi_theory_mcq_source.md` |

---

## To Start App
```bash
/opt/homebrew/bin/streamlit run web/app.py
```
Opens at http://localhost:8501

**Python:** 3.11.15 via Homebrew (`/opt/homebrew/bin/python3.11`). Do NOT use the system 3.9 path (`/Library/Python/3.9/bin/`) — pip is broken there and it doesn't support `X | Y` union type syntax.

---

## Session 5 (preserved)

### IES 2026 — COMPLETE
Backend: 1219 PYQs + rubrics + model answers + 150 MCQs. Web app live on :8501.
No pending tasks for IES.

### UPSC Economics Optional — DATA PIPELINE COMPLETE ✅ | Web app pending

**Final DB state:**
```
pyq_questions:     908
question_rubrics:  908 (100%)
model_answers:     908 (100%)
  upsc_p1:         477/477
  upsc_p2:         431/431
document_chunks:  1,044
topic_base_scores:  16
```

**Next Steps (UPSC):**
Build web app (7_UPSC_Mains.py + 8_UPSC_Model_Answers.py). All data is ready.

**Architecture Decisions (UPSC):**
- DECIDE-01: Separate upsc.db (isolation)
- DECIDE-02: Same 16-table IES schema + 5 new tables
- DECIDE-03: Full text chunking for notes (future RAG)
- DECIDE-04: Skip topper answers + official QPs (scanned/needs_ocr)
- DECIDE-05: Store reference answers separately
