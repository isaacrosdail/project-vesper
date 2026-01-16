"""
WSGI entry point for the Flask application.
Exposes the `app` object for WSGI server to run in production.
"""

from flask_app import app  # noqa: F401
