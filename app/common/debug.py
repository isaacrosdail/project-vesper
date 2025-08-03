import os, sys
from flask import Flask, request

# TODO: Using stderr since Flask buffers print output, but there is undoubtedly a better way to do this.
def print_stderr(msg: str) -> None:
    print(msg, file=sys.stderr)

def print_env_info(app: Flask = None):
    """ Print current env & config info for debugging """
    print_stderr("\n" + "="*20)
    print_stderr("ENVIRONMENT DEBUG INFO")
    print_stderr("="*20)

    # Environment Variables
    print_stderr(f"APP_ENV: {os.environ.get('APP_ENV', "Not set (defaulting to 'dev')")}")
    print_stderr(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")

    # Flask app config
    if app:
        print_stderr(f"\nActive Config: {app.config.get('ENV', 'Not set')}")
        print_stderr(f"DEBUG mode: {app.config.get('DEBUG', False)}")
        print_stderr(f"TESTING mode: {app.config.get('TESTING', False)}")
        print_stderr(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")

    print_stderr("="*20 + "\n")

def debug_config(config_name: str, config_class):
    """ Print which config is being loaded """
    print_stderr(f"\n[CONFIG] Loading {config_name} config: {config_class.__name__}")


def request_debugging(app: Flask = None):
    @app.before_request
    def debug_everything():
        if request.endpoint == 'static':
            return # skip logging for CSS/JS files
        print_stderr(f"\n== REQUEST DEBUG ==")
        print_stderr(f"URL: {request.url}")
        print_stderr(f"Method: {request.method}")
        print_stderr(f"Endpoint: {request.endpoint}")
        print_stderr(f"Form data: {dict(request.form)}")
        print_stderr(f"Args: {dict(request.args)}")
        print_stderr("====================\n")