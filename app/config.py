# Defines environments for database/app stuff (dev vs testing)

class BaseConfig:
    SECRET_KEY = "change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "postgresql://vesper:pass@localhost:5432/vesper" # Using Postgres
    DEBUG = True

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "postgresql://vesper:pass@localhost:5432/vesper_test"
    TESTING = True

config_map = {
    "dev": DevConfig,
    "testing": TestConfig,
    # Future configs here
}