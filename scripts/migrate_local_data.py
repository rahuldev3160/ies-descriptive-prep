"""
Migrate Rahul's local RBI study data to Railway DB.
Links historical rbi_topic_mastery + rbi_attempts (user_id='rahul')
to Rahul's Google account (rahuldevsingh0108@gmail.com).

Run on Railway:
    railway run python scripts/migrate_local_data.py
"""
import sqlite3
from pathlib import Path

_ROOT  = Path(__file__).parent.parent
IES_DB = _ROOT / "data" / "ies.db"
RBI_DB = _ROOT / "data" / "rbi.db"

def main():
    # Step 1: Find Rahul's user_id in ies.db by email
    ies = sqlite3.connect(IES_DB)
    ies.row_factory = sqlite3.Row
    row = ies.execute(
        "SELECT user_id, email FROM users WHERE email=?",
        ("rahuldevsingh0108@gmail.com",)
    ).fetchone()
    ies.close()

    if not row:
        print("ERROR: rahuldevsingh0108@gmail.com not found in users table.")
        print("Make sure Rahul has signed in at least once via Google OAuth before running this.")
        return

    target_user_id = row["user_id"]
    print(f"Found user: {row['email']} → user_id={target_user_id}")

    # Step 2: Update rbi.db rows from user_id='rahul' to target_user_id
    rbi = sqlite3.connect(RBI_DB)

    mastery_count = rbi.execute(
        "SELECT COUNT(*) FROM rbi_topic_mastery WHERE user_id='rahul'"
    ).fetchone()[0]
    attempts_count = rbi.execute(
        "SELECT COUNT(*) FROM rbi_attempts WHERE user_id='rahul'"
    ).fetchone()[0]

    print(f"Migrating {mastery_count} mastery rows + {attempts_count} attempt rows...")

    with rbi:
        rbi.execute(
            "UPDATE rbi_topic_mastery SET user_id=? WHERE user_id='rahul'",
            (target_user_id,)
        )
        rbi.execute(
            "UPDATE rbi_attempts SET user_id=? WHERE user_id='rahul'",
            (target_user_id,)
        )

    remaining = rbi.execute(
        "SELECT COUNT(*) FROM rbi_topic_mastery WHERE user_id='rahul'"
    ).fetchone()[0]
    rbi.close()

    if remaining == 0:
        print(f"Migration complete. {mastery_count} mastery rows + {attempts_count} attempts now linked to {row['email']}.")
    else:
        print(f"WARNING: {remaining} rows still have user_id='rahul'. Check for errors.")

if __name__ == "__main__":
    main()
