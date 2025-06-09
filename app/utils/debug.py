import os
from flask import Flask

def print_env_info(app: Flask = None):
    """ Print current env & config info for debugging """
    print("\n" + "="*20)
    print("ENVIRONMENT DEBUG INFO")
    print("="*20)

    # Environment Variables
    print(f"APP_ENV: {os.environ.get('APP_ENV', "Not set (defaulting to 'dev')")}")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")

    # Flask app config
    if app:
        print(f"\nActive Config: {app.config.get('ENV', 'Not set')}")
        print(f"DEBUG mode: {app.config.get('DEBUG', False)}")
        print(f"TESTING mode: {app.config.get('TESTING', False)}")
        print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")

    print("="*20 + "\n")

def debug_config(config_name: str, config_class):
    """ Print which config is being loaded """
    print(f"\n[CONFIG] Loading {config_name} config: {config_class.__name__}")