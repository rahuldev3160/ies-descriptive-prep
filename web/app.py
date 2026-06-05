"""Flask app factory — entry point for gunicorn (web/wsgi.py)."""
import os
import secrets
import shutil
import sqlite3
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, g, redirect, session

_DATA  = Path(__file__).parent.parent / "data"
_SEEDS = Path(__file__).parent.parent / "seeds"

_ENGLISH_TABLES_SQL = """
    CREATE TABLE IF NOT EXISTS english_question_types (
        type_id TEXT NOT NULL, exam_id TEXT NOT NULL DEFAULT 'english_practice',
        type_name TEXT NOT NULL, description TEXT,
        section_labels_json TEXT, section_weights_json TEXT,
        rubric_type TEXT, sort_order INTEGER DEFAULT 0,
        PRIMARY KEY (type_id, exam_id)
    );
    CREATE TABLE IF NOT EXISTS english_questions (
        question_id TEXT NOT NULL, exam_id TEXT NOT NULL DEFAULT 'english_practice',
        type_id TEXT NOT NULL, prompt_text TEXT NOT NULL,
        marks INTEGER, word_guide_json TEXT, word_count_target INTEGER,
        section_weights_json TEXT, intro_text TEXT, body_text TEXT,
        conclusion_text TEXT, difficulty TEXT DEFAULT 'medium',
        source_exam TEXT, created_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (question_id, exam_id)
    );
    CREATE TABLE IF NOT EXISTS english_keywords (
        keyword_id TEXT NOT NULL, question_id TEXT NOT NULL,
        exam_id TEXT NOT NULL DEFAULT 'english_practice',
        section TEXT NOT NULL CHECK(section IN ('intro','body','conclusion')),
        keyword TEXT NOT NULL, variants_json TEXT, weight INTEGER DEFAULT 1,
        keyword_type TEXT DEFAULT 'required'
            CHECK(keyword_type IN ('required','bonus','negative','phrase')),
        fuzzy_threshold REAL DEFAULT 0.82, penalty REAL,
        PRIMARY KEY (keyword_id, exam_id)
    );
    CREATE TABLE IF NOT EXISTS english_attempts (
        attempt_id TEXT NOT NULL, exam_id TEXT NOT NULL DEFAULT 'english_practice',
        user_id TEXT NOT NULL, question_id TEXT NOT NULL,
        user_answer_intro TEXT, user_answer_body TEXT, user_answer_conclusion TEXT,
        word_count_intro INTEGER DEFAULT 0, word_count_body INTEGER DEFAULT 0,
        word_count_conclusion INTEGER DEFAULT 0,
        score_intro REAL DEFAULT 0.0, score_body REAL DEFAULT 0.0,
        score_conclusion REAL DEFAULT 0.0, auto_score REAL DEFAULT 0.0,
        self_assess_score REAL DEFAULT 0.0,
        keywords_matched_json TEXT, keywords_missed_json TEXT,
        self_assess_json TEXT, session_id TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (attempt_id, exam_id)
    );
    CREATE INDEX IF NOT EXISTS idx_english_attempts_user
        ON english_attempts(user_id, exam_id, created_at DESC);
"""


def _boot_db(name: str) -> None:
    live = _DATA / f"{name}.db"
    seed = _SEEDS / f"{name}_seed.db"
    if live.exists():
        return
    if not seed.exists():
        raise RuntimeError(
            f"data/{name}.db missing and seeds/{name}_seed.db not found. "
            "Run python3 scripts/setup_all.py to initialise."
        )
    shutil.copy(seed, live)


def _run_migrations() -> None:
    db_path = _DATA / "ies.db"
    if not db_path.exists():
        return
    conn = sqlite3.connect(str(db_path))
    try:
        try:
            conn.execute("ALTER TABLE sessions ADD COLUMN remember_me INTEGER DEFAULT 0")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            conn.executescript(_ENGLISH_TABLES_SQL)
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

    _boot_db("ies")
    _boot_db("rbi")
    _boot_db("upsc")
    _run_migrations()

    @app.context_processor
    def inject_globals():
        return {"current_user_id": getattr(g, "user_id", None)}

    @app.before_request
    def open_db():
        from db import _open_conn
        from auth import validate_session
        g.conn = _open_conn()
        g.user_id = None
        token = session.get("session_token")
        if token:
            g.user_id = validate_session(g.conn, token)
            if not g.user_id:
                session.pop("session_token", None)

    @app.teardown_appcontext
    def close_db(exc):
        conn = g.pop("conn", None)
        if conn is not None:
            conn.close()

    from blueprints.auth_bp import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from blueprints.dashboard_bp import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from blueprints.ies_answers_bp import ies_answers_bp
    app.register_blueprint(ies_answers_bp)

    from blueprints.ies_brief_bp import ies_brief_bp
    app.register_blueprint(ies_brief_bp)

    from blueprints.upsc_bp import upsc_bp
    app.register_blueprint(upsc_bp)

    from blueprints.ies_quiz_bp import ies_quiz_bp
    app.register_blueprint(ies_quiz_bp)

    from blueprints.ies_return_quiz_bp import ies_return_quiz_bp
    app.register_blueprint(ies_return_quiz_bp)

    from blueprints.rbi_prep_bp import rbi_prep_bp
    app.register_blueprint(rbi_prep_bp)

    from blueprints.rbi_dashboard_bp import rbi_dashboard_bp
    app.register_blueprint(rbi_dashboard_bp)

    from blueprints.upsc_dashboard_bp import upsc_dashboard_bp
    app.register_blueprint(upsc_dashboard_bp)

    from blueprints.progress_bp import progress_bp
    app.register_blueprint(progress_bp)

    from blueprints.setup_bp import setup_bp
    app.register_blueprint(setup_bp)

    from blueprints.profile_bp import profile_bp
    app.register_blueprint(profile_bp)

    from blueprints.english_bp import english_bp
    app.register_blueprint(english_bp)

    @app.route("/")
    def index():
        if getattr(g, "user_id", None):
            return redirect("/dashboard")
        return redirect("/auth/login")

    return app
