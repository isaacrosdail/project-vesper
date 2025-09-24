from functools import wraps

from flask import abort
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from app.modules.auth.models import User, UserLang, UserRole
from app.modules.auth.repository import UsersRepository
from app.modules.auth.validators import validate_user
from app.shared.database.seed.seed_db import seed_demo_data, seed_rich_data

# TODO: Prune these
# Custom decorator for enforcing owner role permissions
def requires_owner(f):
    """
    Decorator that ensures current_user has OWNER role.

    Returns 403 Forbidden if user lacks owner permissions.
    Must be used after @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user has owner role
        if not current_user.is_owner:
            return abort(403)
        # If they do, call original fuction (ie, proceed)
        return f(*args, **kwargs)
    return decorated_function

def requires_role(role: UserRole):
    """Trying out a decorator factory?"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role):
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_item_ownership(item, user_id):
    """Ensure item belongs to given user. Triggers abort(403) if not."""
    if hasattr(item, 'user_id') and item.user_id != user_id:
        abort(403)

class AuthService:
    # TODO: Extract to notes
    # Dependency injection: session is injected from outside
    # Composition: AuthService "has a" UsersRepository (not "is a")
    def __init__(self, session): # <= inject the session dependency
        self.session = session
        self.users = UsersRepository(session)

    # '*' here is a Python argument marker
    # "Everything after this must be passed by keyword, not by position."
    # eg, this won't work: .register_user("myuser", "blah", "Steve")
    # Must call with explicit keywords
    def register_user(self, *, username: str, password: str, name: str,
                      role: UserRole = UserRole.USER, lang: UserLang = UserLang.EN):
        
        user_data = {
            "username": username,
            "password": password,
            "name": name
        }
        errors = validate_user(user_data)
        if errors:
            return None, errors

        user = User(
            username=username.strip(),
            name=name.strip(),
            role=role.value,
            lang=lang.value
        )
        user.hash_password(password)

        self.users.add(user)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return None, ["Username already exists."]
        
        return user, []
    
    def get_or_create_demo_user(self, seed_data: bool = True):
        """Find existing demo user or create one."""
        # self.users => UsersRepository instance
        # self.users.get_user_by_username => access the method on that instance
        # This is a 'bound method'
        demo_user = self.users.get_user_by_username("guest")

        if demo_user is None:
            demo_user = self.users.create_demo_user()
            self.session.flush()
            if seed_data:
                seed_demo_data(self.session, demo_user.id)
        return demo_user

    def get_or_create_owner_user(self, seed_data: bool = True):
        """Find existing owner user or create one."""
        owner_user = self.users.get_user_by_username("owner")

        if owner_user is None:
            owner_user = self.users.create_owner_user()
            self.session.flush()
            if seed_data:
                seed_rich_data(self.session, owner_user.id)
        return owner_user