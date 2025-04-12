# Defines environments for database/app stuff (dev vs testing)

class BaseConfig:
    SECRET_KEY = "change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "postgresql://vesper:vesperpass@localhost:5432/vesper" # Using Postgres
    DEBUG = True

class TestConfig(BaseConfig):
    # Remove the URI below since PostgreSQL uses dynamic URIs for DBs for testing, not the static one like below
    # SQLALCHEMY_DATABASE_URI = "postgresql://vesper:vesperpass@localhost:5432/vesper_test"
    TESTING = True

config_map = {
    "dev": DevConfig,
    "testing": TestConfig,
    # Future configs here
}