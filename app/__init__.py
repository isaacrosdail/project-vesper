from __future__ import annotations

from datetime import datetime, timedelta
import json
import logging
import secrets
from pathlib import Path
from typing import TYPE_CHECKING, Any
import os
import click
from sqlalchemy.orm import Session
from app.shared.datetime_ import helpers as dth
from app.modules.auth.models import User
from app.modules.auth.repository import UsersRepository
from app.modules.auth.schemas import UserRegister
from app.modules.auth.service import AuthService
from app.shared.database.helpers import delete_all_db_data
from app.shared.database.seed.seed_db import Level, Performance
from app.shared.exceptions import ServiceError
from sqlalchemy.exc import IntegrityError
if TYPE_CHECKING:
    from flask import Response

from alembic.config import Config as AlembicConfig
from flask import Flask, abort, current_app, g, request, url_for
from flask import session as fsession
from flask_caching import Cache
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix

from alembic import command
from app._infra.database import database_connection, db_session, init_db, with_db_session
from app.config import get_config
from app.extensions import _setup_extensions
from app.shared.debug import setup_dev_debugging
from app.shared.serialization import CustomJSONProvider
from app.shared.setup_logging import setup_logging


def has_dev_tools() -> bool:
    """Dev tools visible to anyone in dev, owner-only in prod."""
    if current_app.testing:
        return False
    if current_app.config["APP_ENV"] == "dev":
        return True

    return bool(current_user.is_authenticated and current_user.is_owner)


# Global cache instance? Docs unclear
cache = Cache()


def create_app(config_name: str | None = None) -> Flask:
    """Central app factory. Loads configs, extensions, register blueprints, etc."""

    app = Flask(__name__, template_folder="_templates")
    app.json = CustomJSONProvider(app) # TODO: Name is a WIP obv, rename this

    _apply_config(app, config_name)
    setup_logging(app)  # Must read logging level after being set by apply_config
    if app.config.get("DEBUG"):
        setup_dev_debugging(app)
    _setup_extensions(app)
    _load_asset_manifest(app)
    _setup_request_hooks(app)
    _setup_jinja(app)
    _setup_database(app)
    _register_blueprints(app)
    _register_cli(app)

    return app

def _read_manifest(app: Flask) -> dict[str, str]:
    path = Path(app.static_folder) / "manifest.json"
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}


def _load_asset_manifest(app: Flask) -> None:
    manifest = _read_manifest(app)
    app.config["ASSET_MANIFEST"] = manifest
    app.config["HASHED_ASSETS"] = frozenset(manifest.values())


def _setup_jinja(app: Flask) -> None:
    @app.template_global()
    def asset(name: str) -> str:
        manifest = app.config["ASSET_MANIFEST"] # cached dict at boot
        return url_for("static", filename=manifest.get(name, name))


def _setup_database(app: Flask) -> None:
    """
    Initialize database engine, session, and optionally run migrations.

    Sets up SQLAlchemy engine and configures the database session. If AUTO_MIGRATE is enabled,
    runs Alembic migrations programmatically (equivalent to `alembic upgrade head`)
    Inits database with `app.app_context()`. If app.config's `AUTO_MIGRATE` flag is set to true, then runs
    Alembic migration(s) as well, using `SQLALCHEMY_DATABASE_URI`'s value as `sqlalchemy.url`.

    Note: When running migrations using command.upgrade(), we need to explicitly set `sqlalchemy.url` because
    programmatic calls don't use `alembic/env.py` (unlike CLI commands).

    Registers a teardown handler to clean up database sessions after each request.
    """
    with app.app_context():
        init_db(app.config)
        if app.config["AUTO_MIGRATE"]:
            alembic_cfg = AlembicConfig("alembic.ini")
            alembic_cfg.set_main_option(
                "sqlalchemy.url", app.config["SQLALCHEMY_DATABASE_URI"]
            )
            command.upgrade(alembic_cfg, "head")

        # TODO: fix? Set logging level back after Alembic borks it
        logging.getLogger().setLevel(app.config["LOGGING_LEVEL"])

    # Hook db_session.remove() into teardown
    # Prevents sessions leaking between requests
    @app.teardown_appcontext
    def remove_session(exception=None):  # type: ignore[no-untyped-def]
        db_session.remove()


def _register_blueprints(app: Flask) -> None:
    """
    Imports and register all application blueprints.

    Blueprints are imported here (not at module level) for two reasons:
    1. Ensures setup_logging() runs before blueprint imports, so module-level
    logger = logging.getLogger(__name__) declarations work correctly.
    2. Avoids circular import issues when blueprint files import from app.
    """
    # Import blueprints here so setup_logging() runs BEFORE these imports
    # That way we can have logger = logging.getLogger(__name__) declared top-level in files since it resolves after our logger is set up
    from app.api import api_bp
    from app.devtools.routes import devtools_bp
    from app.errors import errors_bp
    from app.modules.auth.routes import auth_bp
    from app.modules.groceries.routes import groceries_bp
    from app.modules.habits.routes import habits_bp
    from app.modules.metrics.routes import metrics_bp
    from app.modules.tasks.routes import tasks_bp
    from app.modules.time_tracking.routes import time_tracking_bp
    from app.routes import main_bp

    blueprints = [
        main_bp,
        auth_bp,
        api_bp,
        groceries_bp,
        tasks_bp,
        habits_bp,
        metrics_bp,
        time_tracking_bp,
        devtools_bp,
        errors_bp,
    ]
    for bp in blueprints:
        app.register_blueprint(bp)


def _apply_config(app: Flask, config_name: str | None) -> None:
    """
    Copies our config from config_name into app config? (same as current_app?)
    Takes config class (DevConfig, ProdConfig, etc) from config_map & copy all class attrs into app.config
    """
    app.config.from_object(get_config(config_name))

    # For Flask to play nice with CSP headers
    if app.config.get("USE_PROXY_FIX", False):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)


def _setup_request_hooks(app: Flask) -> None:
    """
    Register Flask request lifecycle hooks.

    Namely:
    - before_request: Generates CSP nonce and checks dev tools privileges.
    - context_processor: Injects globals (has_dev_tools, nonce, UserRoleEnum) into all templates
    """

    @app.before_request
    def generate_nonce() -> None:
        g.nonce = secrets.token_urlsafe(16)
        g.has_dev_tools = has_dev_tools()

        if "csrf_token" not in fsession:
            fsession["csrf_token"] = secrets.token_urlsafe(32)
        g.csrf_token = fsession["csrf_token"]

        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not app.testing:
            form_token = (
                request.form.get("csrf_token")
                or (request.get_json(silent=True) or {}).get("csrf_token")  # silent=True for accepting null-bodied apiRequests
                or request.headers.get("X-CSRFToken")
            )
            fsession_token = fsession.get("csrf_token")
            if form_token is None or fsession_token is None:
                abort(403)
            valid = secrets.compare_digest(form_token, fsession_token)
            if not valid:
                abort(403)

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        return {
            "has_dev_tools": g.has_dev_tools,
            "nonce": getattr(g, "nonce", ""),
        }

    # Apply CSP headers
    @app.after_request
    def set_cache_headers(response: Response) -> Response:
        if app.config["APP_ENV"] == "dev":
            return response
        if request.endpoint == "static":
            filename = (request.view_args or {}).get("filename", "")
            if filename in app.config["HASHED_ASSETS"]:
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    @app.after_request
    def apply_csp(response: Response) -> Response:
        if request.endpoint in {"devtools.style_reference", "static"}:
            return response

        nonce = getattr(g, "nonce", "")

        if current_app.config["APP_ENV"] == "dev":
            # Lax dev
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "object-src 'none'; "
                "base-uri 'self';"
            )

        else:
            # Strict prod
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}'; "
                f"style-src 'self' 'nonce-{nonce}'; "
                "img-src 'self' data:; "
                "connect-src 'self'; "       # backend handles external APIs
                "font-src 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "   # anti-clickjacking
                "object-src 'none'; "
                "base-uri 'self'; "          # base tag hijacking
                "upgrade-insecure-requests;" # force HTTPS for HTTP responses
            )
        return response

def _register_cli(app: Flask) -> None:

    @app.cli.command("init-owner")
    def init_owner() -> None:
        with database_connection() as session:
            from app.modules.auth.models import UserRoleEnum
            owner_password = os.environ.get("OWNER_PASSWORD")
            if not owner_password:
                raise click.ClickException("OWNER_PASSWORD not set")
            validated = UserRegister(
                username="owner", password=owner_password, name="Owner", timezone="America/Chicago"
            )
            service = AuthService(session, user_repo=UsersRepository(session))
            try:
                user = service.register_user(validated, role=UserRoleEnum.OWNER)
            except ServiceError:
                raise click.ClickException("User already exists")
            click.echo(f"Owner user ready: {user.username}")

    @app.cli.command("reset-dev")
    @click.confirmation_option(prompt="Delete ALL data?")
    def reset_users() -> None:
        if current_app.config["APP_ENV"] == "prod":
            raise click.ClickException("Operation not allowed")
        with database_connection() as session:
            delete_all_db_data(session, include_users=True, reset_sequences=True)
            click.echo("Users reset!")


    @app.cli.command("seed")
    @click.option("--user-id", type=int, required=True)
    @click.option("--lvl", type=click.Choice(Level, case_sensitive=False), default=Level.MED, required=False)
    @click.option("--perf", type=click.Choice(Performance, case_sensitive=False), default=Performance.AVERAGE, required=False)
    def seed(user_id: int, lvl: Level, perf: Performance) -> None:
        """Seed activity data for a user at a given depth and performance profile."""
        with database_connection() as session:
            from app.shared.database.seed.seed_db import seed_data
            user = session.get(User, user_id)
            if user is None:
                raise click.ClickException(f"No user with id {user_id}")
            try:
                count = seed_data(session, user_id, lvl, perf)
            except IntegrityError as e:
                raise click.ClickException(f"Seed failed on constraint: {e.orig}") from e
            click.echo(f"Seeded {count} records for {user.username}")

    @app.cli.command("reap")
    @click.option("--cutoff", type=int, required=True)
    @with_db_session
    def reap(session: Session, cutoff: datetime) -> None:
        dt = dth.now_utc() - timedelta(days=cutoff)
        repo = UsersRepository(session)
        count = repo.delete_stale_demo_users(dt)
        click.echo(f"Reaped {count} demo users!")
