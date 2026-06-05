"""WSGI entry point for gunicorn.
Run locally: gunicorn --chdir web 'wsgi:app' --bind 0.0.0.0:5000 --reload
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app import create_app

app = create_app()
