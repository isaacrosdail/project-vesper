
class BaseConfig:
    SECRET_KEY = "change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///vesper.db"
    DEBUG = True

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

config_map = {
    "dev": DevConfig,
    "testing": TestConfig,
    # Future configs here
}