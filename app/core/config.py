# Config classes
# Defines environments for database/app stuff (dev vs testing)
import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET-KEY", "change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(BaseConfig):
    ENV = 'development' # Flask-native flag for environment mode: enables debug mode, reloader, detailed error pages
    DEBUG = True # Redundant with ENV, but good for clarity, will remove as I go
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI", "postgresql://user:password@localhost:5432/dbname") # Using Postgres

class ProdConfig(BaseConfig):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")

class TestConfig(BaseConfig):
    ENV = 'testing' # Signals test mode
    TESTING = True  # Enables testing behaviors in Flask (eg, suppress error catching)
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI", "postgresql://user:password@localhost:5432/test_dbname")
    ## Optional upgrades? Study these later
    # WTF_CSRF_ENABLED = False  -> Disable CSRF for form testing
    # DEBUG = False             -> Optional: no need for debug in tests

config_map = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "testing": TestConfig,
    # Future configs here
}