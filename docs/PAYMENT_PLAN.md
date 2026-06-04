# Payment Wallet Feature — Implementation Plan
_Designed: 2026-06-04 · Status: Pre-build (pending Razorpay KYC)_

---

## Gateway: Razorpay (recommended)

| Criterion | Razorpay | Instamojo | Cashfree |
|---|---|---|---|
| Individual account | Yes | Yes | Yes |
| KYC turnaround | 1–3 days | 1–2 days | 1–3 days |
| UPI + Cards + NetBanking | All three | Cards/NetBanking only | All three |
| Embedded checkout | Yes (Checkout.js) | No | Yes |
| Webhook reliability | High + HMAC | Medium | High |
| Python SDK | Best-in-class | Minimal | Good |

**Winner: Razorpay.** Individual PAN + bank account is sufficient. Upgrading to business account later = KYC update only, zero code changes.

**Assumptions to verify at signup:**
- ASSUME-01: Individual account activation 1–3 business days (verify at razorpay.com/docs)
- ASSUME-02: 2% fee on all UPI + card transactions under individual tier
- ASSUME-03: Webhook testing to localhost needs ngrok or Railway public URL

---

## Pricing Model

- Actual cost per grading call: ~₹1.13 (Sonnet: 2000 input + 500 output tokens at $3/$15 MTok)
- **Charge to user: ₹4.50 per answer graded (4× markup)**
- Breakdown shown to user: "₹1.13 → Anthropic AI cost · ₹3.37 → hosting, platform, development"
- ₹100 top-up ≈ 22 answers · ₹500 ≈ 111 answers · ₹2000 ≈ 444 answers

---

## DB Schema (full SQL)

```sql
-- Add to users table
ALTER TABLE users ADD COLUMN wallet_balance_paise INTEGER NOT NULL DEFAULT 0;
ALTER TABLE users ADD COLUMN wallet_grace_until TEXT;  -- ISO datetime, 7-day grace for existing users

-- New: payments table
CREATE TABLE IF NOT EXISTS payments (
    payment_id          TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    razorpay_order_id   TEXT NOT NULL UNIQUE,
    razorpay_payment_id TEXT,
    razorpay_signature  TEXT,
    amount_paise        INTEGER NOT NULL,
    currency            TEXT NOT NULL DEFAULT 'INR',
    status              TEXT NOT NULL DEFAULT 'created',
    -- status: created | authorized | captured | failed | refunded
    webhook_received_at TEXT,
    idempotency_key     TEXT UNIQUE,
    notes               TEXT,  -- JSON
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now')),
    CHECK (status IN ('created','authorized','captured','failed','refunded'))
);
CREATE INDEX IF NOT EXISTS idx_payments_user   ON payments(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_order  ON payments(razorpay_order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status, created_at DESC);

-- New: usage_charges table
CREATE TABLE IF NOT EXISTS usage_charges (
    charge_id       TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    attempt_id      INTEGER,
    feature         TEXT NOT NULL,  -- 'quiz_grading' | 'answer_review' | 'batch_analysis'
    amount_paise    INTEGER NOT NULL,   -- 450 for quiz_grading
    ai_cost_paise   INTEGER NOT NULL,   -- 113 (actual API cost)
    status          TEXT NOT NULL DEFAULT 'pending',
    -- status: pending | deducted | refunded | failed
    balance_before  INTEGER NOT NULL,
    balance_after   INTEGER NOT NULL,
    tokens_input    INTEGER,
    tokens_output   INTEGER,
    model           TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    CHECK (status IN ('pending','deducted','refunded','failed'))
);
CREATE INDEX IF NOT EXISTS idx_charges_user    ON usage_charges(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_charges_attempt ON usage_charges(attempt_id);

-- Config (allows changing price without redeploy)
CREATE TABLE IF NOT EXISTS app_config (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);
INSERT OR IGNORE INTO app_config (key, value) VALUES ('wallet_charge_paise', '450');
```

**Why paise (INTEGER):** SQLite REAL is IEEE 754 float — rounding drift at ₹1.13. INTEGER paise is exact and maps to PostgreSQL BIGINT with zero migration cost.

---

## UX Flow

### Top-up (3 entry points)
1. Dashboard header — wallet widget (balance + "Top Up" button)
2. Quiz page — inline soft banner above submit: "Balance: ₹X · [Top Up]"
3. Sidebar — "Wallet: ₹X" nav item → `10_Wallet.py`

### Top-up steps
1. Amount tiles: ₹100 / ₹200 / ₹500 / ₹1000 / ₹2000 + custom field
2. Backend creates Razorpay Order (server-side, uses `RAZORPAY_KEY_SECRET`)
3. Checkout.js rendered via `st.components.v1.html()` — embedded, no redirect
4. On success: receipt card shown + balance refreshed in session

### Quiz grading steps
1. Below submit: "This answer will cost ₹4.50 · Balance: ₹X"
2. If balance ≥ 450 paise: submit enabled
3. If balance < 450 paise: greyed submit + "Insufficient balance · [Top Up ₹100 →]" (soft prompt, not a wall)
4. On submit: atomic deduction → Claude API call → show result
5. On API failure: synchronous refund of 450 paise + "Grading failed — ₹4.50 refunded"

### Atomic deduction (prevents race condition)
```python
# In a BEGIN IMMEDIATE transaction:
cursor.execute(
    "UPDATE users SET wallet_balance_paise = wallet_balance_paise - 450 "
    "WHERE user_id=? AND wallet_balance_paise >= 450",
    (user_id,)
)
if cursor.rowcount == 0:
    raise InsufficientBalanceError()
```

---

## Wallet Page (10_Wallet.py)

Sections:
1. **Balance card** — ₹X.XX + "~N answers remaining" + [Top Up] + low-balance warning (<₹13.50 = 3 answers)
2. **Top-up UI** — amount tiles + Checkout.js
3. **Receipt** (post-payment) — amount, Razorpay payment_id + order_id, date/time IST, balance after, method
4. **Top-up history** — last 20: date | amount | ref | status | balance after
5. **Usage history** — last 50: date | feature | topic | cost | tokens
6. **Monthly summary** — total spent, answers graded, avg cost, estimated remaining

---

## Webhook Architecture

### Flow
```
Razorpay → POST /api/webhook (Railway URL)
  → Verify HMAC-SHA256 (X-Razorpay-Signature header, raw bytes)
  → Idempotency check (payments.razorpay_order_id already captured?)
  → BEGIN IMMEDIATE
      UPDATE payments SET status='captured', razorpay_payment_id=?
      UPDATE users SET wallet_balance_paise = wallet_balance_paise + amount_paise
  → COMMIT → return 200
```

### Webhook endpoint
Separate `web/webhook.py` (FastAPI/Flask) on port 8502. Added to Procfile alongside Streamlit. Railway exposes both ports.

### HMAC verification
```python
import hmac, hashlib
def verify_razorpay_webhook(payload_body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
# payload_body = raw bytes BEFORE json.loads()
```

---

## Edge Cases

| # | Scenario | Resolution |
|---|---|---|
| 1 | Webhook never fires | Manual reconcile script `scripts/reconcile_payment.py --payment-id X --user-id Y`; cron job to backfill captured orders |
| 2 | API fails after deduction | Synchronous refund in exception handler; charge status → 'refunded' |
| 3 | Two tabs submit simultaneously | Atomic `UPDATE WHERE balance >= 450`; rowcount check; second tab gets "Insufficient balance" |
| 4 | Razorpay downtime | Reuse existing order_id (valid 15 min); show "Payment service unavailable, retry in a few minutes" |
| 5 | Chargeback | `usage_charges` table is evidence log; keep forever; never delete |
| 6 | Balance goes negative | `WHERE wallet_balance_paise >= 450` prevents this; add `CHECK (wallet_balance_paise >= 0)` constraint |
| 7 | Personal → institutional account | Env var swap only (`RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`); zero code changes |
| 8 | Existing users locked out at launch | 7-day grace: `wallet_grace_until = now + 7 days`; banner "Free until [date]" |

---

## Scale Path (decisions to make NOW)

### Gateway abstraction layer (`web/billing.py`)
```python
# All quiz/wallet pages import from here — never from razorpay directly
def create_order(user_id, amount_paise) -> str: ...
def verify_webhook(payload, signature) -> bool: ...
def fetch_payment_status(payment_id) -> str: ...
def issue_refund(payment_id, amount_paise) -> bool: ...
```
30 minutes to write; saves full rewrite if gateway ever changes.

### Subscription tier coexistence
When flat subscription is added: `if subscription_tier == 'pro': skip_deduction`. `usage_charges` still logs the call for analytics.

### PostgreSQL migration
- All PKs are `TEXT` (UUIDs), not AUTOINCREMENT
- Use `datetime.utcnow().isoformat()` in Python, not `datetime('now')` SQLite default
- `wallet_balance_paise BIGINT` in PostgreSQL — exact match

---

## Implementation Sequence

| Step | Task | Hours |
|---|---|---|
| 1 | Razorpay signup + KYC (external, start now) | 1h |
| 2 | DB migrations (ALTER users, payments, usage_charges, app_config) | 1h |
| 3 | `web/billing.py` abstraction layer | 2h |
| 4 | `web/webhook.py` FastAPI endpoint + HMAC + idempotency | 3h |
| 5 | Railway: webhook service config + register URL in Razorpay | 1h |
| 6 | `web/pages/10_Wallet.py` full UI + Checkout.js + receipt | 4h |
| 7 | Dashboard wallet widget in `app.py` | 1h |
| 8 | Quiz gate: balance check + atomic deduction + refund on failure | 3h |
| 9 | Grace period migration + banner | 1h |
| 10 | `9_Answer_Review.py` actual implementation + same billing | 3h |
| 11 | `scripts/reconcile_payment.py` | 1h |
| 12 | End-to-end test (test mode) | 2h |
| 13 | Go live: switch to Razorpay live mode + real ₹1 test | 1h |

**Total: ~23 hours · ~8–9 days at 2–4h/day**

**Critical path:** Start Razorpay KYC immediately (1–3 day external wait). Build Steps 2–6 while waiting — all code, no gateway needed until Step 5.
