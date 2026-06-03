---
description: Run and visually test the Descriptive Exams Streamlit app. Use when asked to run, start, verify, or screenshot any page in this app.
---

# Run & Test — Descriptive Exams App

## Start the server

```bash
pkill -f "streamlit run" 2>/dev/null
cd "/Users/rahulsingh/Desktop/Claude Projects/Descriptive-exams/web"
/opt/homebrew/bin/streamlit run app.py \
  --server.port 8501 --server.headless true &>/tmp/streamlit_app.log &
sleep 4
curl -s http://localhost:8501 | head -3   # confirm "Streamlit" in response
```

## Error triage — MANDATORY before touching any code

When a page crashes, run this before editing anything:

```bash
# Step 1 — read the full traceback
cat /tmp/streamlit_app.log | grep -A10 "Traceback\|Error"

# Step 2 — classify the error
# TypeError: unsupported operand type(s) for | → Python VERSION mismatch, not a code bug
# ImportError / ModuleNotFoundError             → wrong Python env, check which streamlit
# KeyError / AttributeError                     → logic bug, safe to fix directly

# Step 3 — if TypeError with | operator: confirm runtime before touching code
/opt/homebrew/bin/streamlit --version   # must say Python 3.11
which streamlit                          # must resolve to /opt/homebrew/bin/streamlit
```

**Rule:** If `TypeError.*unsupported.*|` appears in the traceback, the fix is NEVER "remove the annotation." The fix is confirming the server is running on `/opt/homebrew/bin/streamlit` (Python 3.11). Removing the annotation is a symptom suppression — it masks the root cause and will recur on the next file that uses modern syntax.

## Pages & what they do

| Sidebar label | File | Key things to test |
|---|---|---|
| app | `web/app.py` | Dashboard loads, readiness % shows |
| Model Answers | `web/pages/1_Model_Answers.py` | Question browse, no DB errors |
| Quiz | `web/pages/2_Quiz.py` | Quiz loads, Anthropic key reachable |
| Study Brief | `web/pages/3_Study_Brief.py` | Topic briefs load |
| My Progress | `web/pages/4_My_Progress.py` | Attempt history renders |
| Return Quiz | `web/pages/5_Return_Quiz.py` | MCQ form loads |
| RBI Prep | `web/pages/6_RBI_Prep.py` | 4 tabs: Key Data / Phase 1 Drill / Tier 2 Quiz / My Progress |

## RBI Prep tab structure (6_RBI_Prep.py)

- **Key Data** — static rate cards; no DB needed
- **Phase 1 Drill** — reads from `data/rbi.db`, 267 tier-1 questions; Smart Serve or Filter mode
- **Tier 2 Quiz** — 54 hardcoded MCQs, 9 buckets, no DB; instant grading
- **My Progress** — reads rbi_topic_mastery from rbi.db; requires ≥1 drill attempt

## Playwright interaction patterns

**CRITICAL:** Streamlit widgets are CSS-hidden React components. Use `data-testid` selectors.

```python
from playwright.async_api import async_playwright
import asyncio

async def test_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        # Navigate sidebar
        await page.get_by_text("RBI Prep", exact=True).first.click()
        await page.wait_for_timeout(2000)

        # Switch tab — use get_by_role("tab"), NOT get_by_text (strict-mode ambiguity)
        await page.get_by_role("tab", name="Tier 2 Quiz").click()
        await page.wait_for_timeout(2000)

        # Click radio buttons — use [data-testid="stRadio"] groups
        groups = page.locator("[data-testid='stRadio']")
        for i in range(await groups.count()):
            try:
                await groups.nth(i).locator("label").first.click(timeout=5000)
            except:
                # Scroll main container, retry
                await page.evaluate(
                    f"document.querySelectorAll('[data-testid=\"stRadio\"]')[{i}]"
                    "?.querySelector('label')?.scrollIntoView()"
                )
                await page.wait_for_timeout(150)
                try:
                    await groups.nth(i).locator("label").first.click(timeout=3000)
                except:
                    pass

        # Submit
        await page.get_by_role("button", name="Submit →").click()
        await page.wait_for_timeout(5000)

        # Verify results — look for expanders
        expanders = page.locator("details")
        count = await expanders.count()
        assert count > 0, "No result expanders — submit may have failed"

        # Check for Python errors on page
        body = await page.content()
        assert "KeyError" not in body and "Traceback" not in body

        await page.screenshot(path="/tmp/test_result.png")
        await browser.close()

asyncio.run(test_page())
```

## Reusable helpers

Import from `scripts/streamlit_test_utils.py`:

```python
from scripts.streamlit_test_utils import (
    start_server, navigate_to_page, click_tab,
    answer_radio_groups, submit_form, check_for_errors,
    get_expander_count
)
```

## Databases

| DB | Tables to check |
|---|---|
| `data/rbi.db` | rbi_questions (267+36), rbi_attempts, rbi_topic_mastery |
| `data/ies.db` | questions, rubrics, model_answers, attempts |
| `data/upsc.db` | same schema as ies.db |

Quick sanity:
```bash
sqlite3 data/rbi.db "SELECT tier, COUNT(*) FROM rbi_questions GROUP BY tier;"
sqlite3 data/ies.db "SELECT COUNT(*) FROM questions;"
```

## Bug status (updated Session 8 — 2026-06-03)

### IES pages — ALL CRITICAL/HIGH BUGS FIXED ✅ (Session 8)
Smoke test: **11/11 PASS**

| Bug | Status | Fix applied |
|---|---|---|
| Connection leak — per-rerun `get_conn()` | ✅ FIXED | `@st.cache_resource` on `_get_conn()` in all 5 pages; all `conn.close()` removed |
| Silent quiz save failure `2_Quiz.py:532` | ✅ FIXED | `except: pass` → `st.toast(err)` |
| Mastery not written on first attempt | ✅ FIXED | `INSERT OR IGNORE` + `UPDATE` pattern in `submit_return_quiz` |
| No transaction in `submit_return_quiz` | ✅ FIXED | All writes in `with conn:` atomic block |
| FD leak in `@st.cache_data` `2_Quiz.py:92` | ✅ FIXED | `try/finally c.close()` |
| Option sort scramble `5_Return_Quiz.py` | ✅ FIXED | `sorted()` on full string, not first char |

### Open issues

**RISK-02 (live bug): `6_RBI_Prep.py:21` — `USER_ID = "rahul"` hardcoded**
All RBI drill attempts from any user are saved as "rahul". All users see Rahul's RBI My Progress data.
Fix: replace `USER_ID = "rahul"` with `get_user_id()` from `db.py`. Item #1 in the MVMU list.

**ARCHITECTURAL NOTE: `@st.cache_resource` is single-user only**
The Session 8 connection fix (`@st.cache_resource` on `_get_conn()`) eliminates the per-rerun leak but creates a shared Python `sqlite3.Connection` object across all concurrent users. Python's sqlite3 is NOT thread-safe at the connection-object level — concurrent writes from two users on the same connection can corrupt cursor state or transaction boundaries.

**This is safe for single-user use.** Before going multi-user, revert to per-request connections:
```python
conn = get_conn()
try:
    # all page logic
finally:
    conn.close()
```
And add to `get_conn()`: `conn.execute("PRAGMA journal_mode=WAL"); conn.execute("PRAGMA busy_timeout=5000")`

Full multi-user plan: `memory/project_multiuser_plan.md`
