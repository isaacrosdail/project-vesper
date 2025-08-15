"""
Flask extensions initialized here to avoid circular imports.
Import these in other modules instead of importing from app.
"""

from flask_caching import Cache
from flask_login import LoginManager

# Create extension instances
cache = Cache()
login_manager = LoginManager()

def _setup_extensions(app):

    login_manager.init_app(app)
    login_manager.login_view = "auth.login" # <- where @login_required redirects

    # Flask-Login needs this callback
    # Note: this runs outside the normal request flow? Called whenever Flask-Login needs to reload the user object, even between requests.
    @login_manager.user_loader
    def load_user(user_id):
        from app._infra.database import db_session
        from app.modules.auth.models import User
        return db_session.get(User, int(user_id))
    
    # Init Flask-Caching
    app.config.from_mapping({
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 300,
    })
    cache.init_app(app)
