# PLAN-005 — English Practice Module

**Date:** 2026-06-05 (Session 15 planning)
**Status:** APPROVED — hybrid scoring confirmed; Option C content seeding
**Agents used:** 4 parallel (Taxonomy, Format Templates, Codebase Integration, Scoring Algorithm)

---

## Critical Finding: IES Disambiguation

"IES" in the app = **Indian Economic Service** (not Engineering Services/ESE).
- IES Economic Service: Has a General English paper (100m, 3hr) — Essay, Précis, RC, Vocabulary
- IES Engineering Services/ESE: No English paper whatsoever. Paper I = GS+Engineering MCQ only.

The existing app (economics topics, Papers II/III/IV) correctly targets IES Economic Service. The English module is in scope for this exam.

---

## Final Question Type Taxonomy (7 Clusters)

| # | Type | Exams | Marks | Freq | Scoreable? |
|---|------|-------|-------|------|------------|
| 1 | **Essay** | IES Eco + RBI Ph.II + UPSC Paper B + UPSC Essay Paper | 40–125m | HIGH (all exams) | Yes — section keywords |
| 2 | **Précis** | IES Eco + RBI Ph.II + UPSC Paper B | 30–75m | HIGH (all exams) | Yes — best candidate (highly mechanical conventions) |
| 3 | **Reading Comprehension** | IES Eco + RBI Ph.II + UPSC Paper B | 30–75m | HIGH (all exams) | Partial — per-question keywords (different schema needed) |
| 4 | **Formal Letter** | UPSC Paper B (~3/10 papers) | 15–20m | LOW | Yes — format + keywords |
| 5 | **Report Writing** | UPSC Paper B (~2/10 papers) | 15–20m | LOW | Yes — format + keywords |
| 6 | **Grammar & Usage** | UPSC Paper B (40m), IES Eco | 40–50m | MEDIUM | Hard without AI — sentence transformation can't be pattern-matched |
| 7 | **MCQ Vocabulary/Grammar** | RBI Ph.I (30m MCQ), IES ESE | N/A | HIGH (RBI) | Yes — MCQ, different system |

**Notes:**
- Letter/Report NOT in current RBI Grade B pattern (confirmed). UPSC only, rare.
- Translation: Conflicting research — Agent A says it is Paper A (Indian Language), not Paper B (English). Treat as out of scope pending verification.
- Grammar/Usage (Type 6): 40/300 marks UPSC, but subjective transformation tasks (active/passive, speech conversion) can't be keyword-scored reliably. Phase 2 at earliest.
- MCQ Type 7: Needs a separate MCQ quiz mode, not the section-based scoring system.

---

## Recommended Implementation Scope

### Phase 1 — Build these first (highest marks × highest frequency)
1. **Essay** — universal, 40–125m, clear intro/body/conclusion structure
2. **Précis** — universal, 30–75m, most mechanical (title, word count, third person = auto-checkable)
3. **Reading Comprehension** — universal, 30–75m, per-question model (see RC schema note below)

### Phase 2 — Add after Phase 1 validated
4. Formal Letter (UPSC only, format-heavy)
5. Report Writing (UPSC only, format-heavy)
6. Grammar/Usage — possibly self-assessment only (show correct transformation, user ticks)

### Out of scope (this iteration)
- MCQ Vocabulary/Grammar (different system, not section-based)
- Translation (exam scope unclear, requires bilingual content)

---

## Architecture

### New page
- File: `web/pages/11_English_Practice.py`
- Nav group: Practice (alongside Quiz, Return Quiz, RBI Prep)
- Auth: `require_user(conn)` mandatory — no BUG-012 repeat

### New tables (all in ies.db, exam_id='english_practice')

```sql
CREATE TABLE IF NOT EXISTS english_question_types (
    type_id     TEXT NOT NULL,
    exam_id     TEXT NOT NULL DEFAULT 'english_practice',
    type_name   TEXT NOT NULL,       -- 'Essay', 'Précis', 'RC', 'Formal Letter', etc.
    description TEXT,
    sort_order  INTEGER DEFAULT 0,
    PRIMARY KEY (type_id, exam_id)
);

CREATE TABLE IF NOT EXISTS english_questions (
    question_id      TEXT NOT NULL,
    exam_id          TEXT NOT NULL DEFAULT 'english_practice',
    type_id          TEXT NOT NULL,
    prompt_text      TEXT NOT NULL,
    marks            INTEGER,
    word_guide_json  TEXT,           -- JSON: {"intro":80,"body":340,"conclusion":80}
    section_weights_json TEXT,       -- JSON: {"intro":0.15,"body":0.70,"conclusion":0.15}
    intro_text       TEXT,
    body_text        TEXT,
    conclusion_text  TEXT,
    difficulty       TEXT DEFAULT 'medium',  -- easy/medium/hard
    source_exam      TEXT,           -- 'rbi_2024', 'upsc_2023', etc.
    created_at       TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (question_id, exam_id)
);

-- Keyword tags per section for offline scoring
CREATE TABLE IF NOT EXISTS english_keywords (
    keyword_id     TEXT NOT NULL,
    question_id    TEXT NOT NULL,
    exam_id        TEXT NOT NULL DEFAULT 'english_practice',
    section        TEXT NOT NULL CHECK(section IN ('intro','body','conclusion')),
    keyword        TEXT NOT NULL,
    variants_json  TEXT,             -- JSON array: ["term", "terms", "abbreviation"]
    weight         INTEGER DEFAULT 1,  -- 1=standard, 2=critical
    keyword_type   TEXT DEFAULT 'required' CHECK(keyword_type IN ('required','bonus','negative','phrase')),
    fuzzy_threshold REAL DEFAULT 0.82,
    PRIMARY KEY (keyword_id, exam_id)
);

-- Practice attempts with offline keyword scores
CREATE TABLE IF NOT EXISTS english_attempts (
    attempt_id              TEXT NOT NULL,
    exam_id                 TEXT NOT NULL DEFAULT 'english_practice',
    user_id                 TEXT NOT NULL,
    question_id             TEXT NOT NULL,
    user_answer_intro       TEXT,
    user_answer_body        TEXT,
    user_answer_conclusion  TEXT,
    word_count_intro        INTEGER DEFAULT 0,
    word_count_body         INTEGER DEFAULT 0,
    word_count_conclusion   INTEGER DEFAULT 0,
    score_intro             REAL DEFAULT 0.0,   -- 0.0–10.0
    score_body              REAL DEFAULT 0.0,
    score_conclusion        REAL DEFAULT 0.0,
    score_overall           REAL DEFAULT 0.0,
    keywords_matched_json   TEXT,   -- JSON: {"intro":["term1"],"body":[...],"conclusion":[...]}
    keywords_missed_json    TEXT,
    session_id              TEXT,
    created_at              TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (attempt_id, exam_id)
);

CREATE INDEX IF NOT EXISTS idx_english_attempts_user
    ON english_attempts(user_id, exam_id, created_at DESC);
```

### RC special handling

RC questions don't fit intro/body/conclusion — each sub-question has its own independent answer. Two options:

**Option A (simpler — recommended for Phase 1):** Store each RC sub-question as a separate `english_question` with only the `body` section. The `intro_text` stores the passage (shared across sub-questions), `body_text` is the model answer per question, `conclusion_text` is empty. The passage is linked via a parent `question_id` stored in `source_exam` or a new `passage_id` column.

**Option B (cleaner but more schema work):** Separate `english_passages` table (passage_id, passage_text) → `english_questions` has `passage_id` FK. Used by all sub-questions referencing that passage.

Option A is sufficient for Phase 1. Add Option B when RC volume justifies it.

---

## Scoring Module

### File layout (new)
```
scoring/
├── __init__.py
├── keyword_scorer.py     # score_section(), score_answer(), build_feedback()
├── normaliser.py         # normalize(), _expand_abbreviations(), ABBREVIATION_MAP
├── constants.py          # section weight defaults per question type
└── validator.py          # validate_keyword_schema() for content QA
```

### Algorithm (pure Python, no ML)
1. **Normalise**: lowercase → expand abbreviations (GDP→ gross domestic product) → strip punctuation
2. **Required keywords**: exact substring + sliding-window fuzzy (difflib.SequenceMatcher, threshold 0.82)
3. **Bonus keywords**: same matching, contribute ≤15% of section score
4. **Phrases**: exact contiguous match after normalisation
5. **Negative keywords**: detected misconceptions, penalty up to -0.4 on section score
6. **Section score**: `min((req_score × 0.85) + bon_contrib + phrase_contrib, 1.0) - penalty`
7. **Overall score**: section scores × section weights (normalised)

### Section weight defaults by type

| Type | Intro | Body | Conclusion |
|------|-------|------|------------|
| Essay (analytical) | 15% | 70% | 15% |
| Essay (UPSC extended) | 20% | 60% | 20% |
| Précis | 10% | 80% | 10% |
| RC answer | — | 100% | — |
| Letter / Report | 5% | 85% | 10% |

Weights stored per-question in `section_weights_json` — not hardcoded.

### Content pipeline
Keyword tagging is a Haiku batch job (extend existing `generate_rubrics.py` pipeline):
- Input: model answer intro/body/conclusion for each question
- Output: `keyword_schema` JSON per section (required, bonus, negative, phrases)
- Validation: `validate_keyword_schema()` flags < 2 required keywords or > 14 required keywords per section
- Storage: `english_keywords` table rows (normalized from the JSON)

---

## Reuse from Existing Code (do not reinvent)

| Component | Source | Reuse |
|-----------|--------|-------|
| Three-section answer form | `2_Quiz.py` lines 443–468 | Copy exactly; remove `disabled=True` |
| Section-color answer renderer | `1_Model_Answers.py::_render_answer_sections()` | Call directly |
| Score card display | `2_Quiz.py` + `styles.py::score_card_html()` | Call with section labels |
| CSS classes (gem-card, chip, section-header) | `styles.py::apply_theme()` | Call at page top |
| `jl()` JSON parser | `db.py` | Import for keywords_matched_json |
| `track_page_time()` | `db.py` | Call with "English Practice" |
| `log_event()` | `db.py` | Call on each submission |
| `@st.cache_data(ttl=300)` | `2_Quiz.py` | Same pattern for question loader |

---

## Integration Risks

**RISK-1 (HIGH) — BUG-010/011: user_id fallback**
The new page must call `require_user(conn)` and pass `user_id` explicitly to every DB write. Never call `get_user_id()` inside English module helpers — it has the "rahul" literal fallback.

**RISK-2 (MEDIUM) — NAV-001: nav branch timing**
Page must be in the authenticated branch only in `app.py`. Test cookie-restore path to verify page is accessible after cold login.

**RISK-3 (PRODUCT) — Keyword false negatives cause user distrust**
Correct paraphrase that hits no keywords will score 0%. Surface this clearly: label the score "Keyword Coverage" not "Answer Score". Show which keywords were hit and missed. Instruct content creators to include 3–5 variants per keyword (including mechanism-level variants, not just the canonical term).

---

## Open Decisions (for Rahul)

1. **RC schema (Phase 1):** Use Option A (body-only questions) or Option B (separate passage table)? Option A is simpler now, Option B is cleaner long-term.
2. **Grammar/Usage (Phase 1 or 2):** Include as self-assessment (show correct transformation, user marks themselves) or skip entirely for Phase 1?
3. **Content seeding:** AI-generate model answers + keyword tags via Haiku batch (fast, ~100 questions in one batch run), or manually curate a smaller set (20–30 questions) to validate the system first?
4. **Letter/Report:** Include in Phase 1 (UPSC users want this) or Phase 2?
