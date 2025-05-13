# Config classes
# Defines environments for database/app stuff (dev vs testing)

class BaseConfig:
    SECRET_KEY = "change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(BaseConfig):
    ENV = 'development' # Flask-native flag for environment mode: enables debug mode, reloader, detailed error pages
    DEBUG = True # Redundant with ENV, but good for clarity, will remove as I go
    SQLALCHEMY_DATABASE_URI = "postgresql://vesper:pass@localhost:5432/vesper" # Using Postgres

class TestConfig(BaseConfig):
    ENV = 'testing' # Signals test mode
    TESTING = True  # Enables testing behaviors in Flask (eg, suppress error catching)
    SQLALCHEMY_DATABASE_URI = "postgresql://vesper:pass@localhost:5432/vesper_test"
    ## Optional upgrades? Study these later
    # WTF_CSRF_ENABLED = False  -> Disable CSRF for form testing
    # DEBUG = False             -> Optional: no need for debug in tests

config_map = {
    "dev": DevConfig,
    "testing": TestConfig,
    # Future configs here
}