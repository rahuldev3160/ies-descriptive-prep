"""
Print N random MCQs from return_quiz_questions for manual validation.
Usage: python3.11 scripts/spot_check_mcq.py [--n 10] [--paper ge_01]
"""
import argparse
import random
import sqlite3
from pathlib import Path

DB = Path(__file__).parent.parent / "data" / "ies.db"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10, help="Number of questions to sample")
    ap.add_argument("--paper", default=None, help="Filter by paper_id e.g. ge_01")
    ap.add_argument("--topic", default=None, help="Filter by topic_id")
    args = ap.parse_args()

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    query = """
        SELECT rq.question_id, rq.topic_id, rq.question_text,
               rq.correct_answer, rq.option_b, rq.option_c, rq.option_d,
               rq.difficulty,
               t.paper_id
        FROM return_quiz_questions rq
        JOIN topics t ON rq.topic_id = t.topic_id AND rq.exam_id = t.exam_id
        WHERE rq.exam_id = 'ies_2026'
    """
    params = []
    if args.paper:
        query += " AND t.paper_id = ?"
        params.append(args.paper)
    if args.topic:
        query += " AND rq.topic_id = ?"
        params.append(args.topic)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    if not rows:
        print("No questions found.")
        return

    sample = random.sample(rows, min(args.n, len(rows)))
    print(f"\n{'='*70}")
    print(f"MCQ SPOT CHECK — {len(sample)} questions sampled from {len(rows)} total")
    print(f"{'='*70}\n")

    wrong = 0
    for i, q in enumerate(sample, 1):
        # correct_answer is option A (correct); option_b/c/d are distractors
        opts = [q["correct_answer"], q["option_b"], q["option_c"], q["option_d"]]
        print(f"Q{i}. [{q['paper_id'].upper()} | {q['topic_id']} | diff:{q['difficulty']}]")
        print(f"    {q['question_text']}")
        for label, opt in zip(["(correct→)", "        B:", "        C:", "        D:"], opts):
            if opt:
                print(f"    {label} {opt[:100]}{'...' if len(opt) > 100 else ''}")
            else:
                print(f"    {label} ⚠ MISSING")
        print()

        missing = sum(1 for o in opts[1:] if not o)
        if missing:
            print(f"    ⚠ {missing} distractor option(s) missing")
            wrong += 1

    print(f"{'='*70}")
    print(f"Issues flagged: {wrong}/{len(sample)}")
    if wrong:
        print("⚠ Check flagged questions — correct_answer must start with A)/B)/C)/D)")


if __name__ == "__main__":
    main()
