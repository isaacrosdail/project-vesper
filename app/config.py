"""
Configuration classes for different environments.
Manages database URIs, debug settings, and environment-specific settings.
"""
import os, logging
from datetime import timedelta
from dotenv import load_dotenv
from flask.config import Config  # hijack Flask's config obj

# Only load .env in non-prod
if os.getenv("APP_ENV", "dev") != "prod":
    load_dotenv(override=False) # real env (Docker) wins if already set, so we pull our env vars from our container instead of 

class BaseConfig:
    LOGGING_LEVEL = logging.INFO
    DEFAULT_TZ = "Europe/London" # default TZ to be used for some stuff
    APP_ENV = "base"
    AUTO_MIGRATE = True     # Default to run migrations on startup
    USE_PROXY_FIX = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=30) # Flask automatically picks this up

class DevConfig(BaseConfig):
    LOGGING_LEVEL = logging.DEBUG
    APP_ENV = "dev"
    DEBUG = True            # Enables debug mode, reloader, detailed error pages
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URI",
        "postgresql://user:password@localhost:5432/dbname"
    )
    SQLALCHEMY_ECHO = False # flip to True to see SQL sent by SQLAlchemy

class ProdConfig(BaseConfig):
    LOGGING_LEVEL = logging.WARNING
    APP_ENV = "prod"
    AUTO_MIGRATE = True
    USE_PROXY_FIX = True   # For playing nice with our CSP/nginx headers
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")

class TestConfig(BaseConfig):
    APP_ENV = "testing"
    TESTING = True          # Enables testing behaviors in Flask (eg, suppress error catching)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URI",
        "postgresql://user:password@localhost:5432/test_dbname"
    )
    # DEBUG = False             # Optional: Disable debug in tests

config_map = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "testing": TestConfig,
}