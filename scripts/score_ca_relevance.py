"""
Score CA (current affairs) relevance for each IES topic using Claude Haiku.
Updates ca_relevance_score and recomputes base_priority_score in topic_base_scores.

Run: python3.11 scripts/score_ca_relevance.py
"""
import os
import sqlite3
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()
# Fallback: load from Devthorium project .env (where the key actually lives)
_devthorium_env = Path.home() / "Desktop" / "Claude Projects" / "Devthorium" / ".env"
if not os.environ.get("ANTHROPIC_API_KEY") and _devthorium_env.exists():
    load_dotenv(_devthorium_env)

DB_PATH = Path(__file__).parent.parent / "data" / "ies.db"
CA_DATA_PATH = Path(__file__).parent.parent / "data" / "rbi_current_data.txt"
EXAM_ID = "ies_2026"
MODEL = "claude-haiku-4-5-20251001"

PROMPT_TEMPLATE = """\
CA data (excerpt): {ca_excerpt}

Topic: {topic_name}

Score 0.0-1.0: how relevant is current affairs economic data to this topic?
0.0 = pure theory, no CA overlap. 1.0 = directly tested via CA data.
Reply with only the float score, nothing else."""


def load_topics(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    rows = conn.execute(
        "SELECT topic_id, topic_name, paper_id FROM topics "
        "WHERE exam_id=? AND topic_level='topic' ORDER BY paper_id, topic_id",
        (EXAM_ID,),
    ).fetchall()
    return rows


def load_ca_excerpt(path: Path, max_chars: int = 800) -> str:
    text = path.read_text(encoding="utf-8")
    return text[:max_chars]


def score_topic(client: anthropic.Anthropic, topic_name: str, ca_excerpt: str) -> float:
    prompt = PROMPT_TEMPLATE.format(ca_excerpt=ca_excerpt, topic_name=topic_name)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    try:
        return max(0.0, min(1.0, float(raw)))
    except ValueError:
        # Extract first float-like token if the model adds extra text
        for token in raw.split():
            try:
                return max(0.0, min(1.0, float(token)))
            except ValueError:
                continue
        print(f"  [WARN] Could not parse score '{raw}' for '{topic_name}', defaulting 0.0")
        return 0.0


def update_ca_score(conn: sqlite3.Connection, topic_id: str, score: float) -> None:
    conn.execute(
        "UPDATE topic_base_scores SET ca_relevance_score=? WHERE topic_id=? AND exam_id=?",
        (score, topic_id, EXAM_ID),
    )


def recompute_base_priority(conn: sqlite3.Connection) -> None:
    cfg = conn.execute(
        "SELECT w1_pyq_recurrence, w2_pyq_recency, w3_concept_persistence, "
        "w4_ca_relevance, w5_syllabus_weight, w6_graph_centrality "
        "FROM exam_configurations WHERE exam_id=?",
        (EXAM_ID,),
    ).fetchone()
    W1, W2, W3, W4, W5, W6 = cfg if cfg else (0.22, 0.20, 0.10, 0.08, 0.12, 0.08)

    active_weight_sum = W1 + W2 + W3 + W4 + W5 + W6

    rows = conn.execute(
        "SELECT topic_id, pyq_recurrence_score, pyq_recency_score, "
        "concept_persistence_score, ca_relevance_score, "
        "graph_centrality_score FROM topic_base_scores WHERE exam_id=?",
        (EXAM_ID,),
    ).fetchall()

    for topic_id, w1, w2, w3, w4, w6 in rows:
        # w5 lives in the topics table — fetch it
        w5_row = conn.execute(
            "SELECT syllabus_weight FROM topics WHERE topic_id=? AND exam_id=?",
            (topic_id, EXAM_ID),
        ).fetchone()
        w5 = w5_row[0] if w5_row else 0.0

        base = (W1 * w1 + W2 * w2 + W3 * w3 + W4 * w4 + W5 * w5 + W6 * w6) / active_weight_sum
        conn.execute(
            "UPDATE topic_base_scores SET base_priority_score=?, computed_at=datetime('now') "
            "WHERE topic_id=? AND exam_id=?",
            (round(base, 4), topic_id, EXAM_ID),
        )


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY not set. Add it to .env or the environment.")

    client = anthropic.Anthropic(api_key=api_key)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")

    topics = load_topics(conn)
    ca_excerpt = load_ca_excerpt(CA_DATA_PATH)

    print(f"Scoring {len(topics)} topics for CA relevance...\n")
    print(f"{'topic_id':<45} {'paper':<8} {'score':>6}")
    print(f"{'─'*45} {'─'*8} {'─'*6}")

    scores: dict[str, float] = {}
    for topic_id, topic_name, paper_id in topics:
        score = score_topic(client, topic_name, ca_excerpt)
        scores[topic_id] = score
        update_ca_score(conn, topic_id, score)
        print(f"  {topic_id:<43} {paper_id:<8} {score:.2f}")
        time.sleep(0.5)

    conn.commit()

    print("\nRecomputing base_priority_score with w4 included...")
    recompute_base_priority(conn)
    conn.commit()

    # Summary table sorted by CA score descending
    rows = conn.execute(
        "SELECT topic_id, ca_relevance_score, base_priority_score "
        "FROM topic_base_scores WHERE exam_id=? ORDER BY ca_relevance_score DESC",
        (EXAM_ID,),
    ).fetchall()

    print(f"\n{'─'*65}")
    print(f"{'FINAL SUMMARY — CA Relevance Scores':^65}")
    print(f"{'─'*65}")
    print(f"  {'topic_id':<43} {'ca_score':>8} {'priority':>8}")
    print(f"  {'─'*43} {'─'*8} {'─'*8}")
    for topic_id, ca_score, priority in rows:
        print(f"  {topic_id:<43} {ca_score:>8.2f} {priority:>8.4f}")

    conn.close()
    print(f"\nDone. {len(scores)} topics scored and base_priority_score recomputed.")


if __name__ == "__main__":
    main()
