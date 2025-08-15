import sys

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app._infra.database import database_connection, with_db_session
from app.modules.auth.models import UserRole
from app.modules.auth.repository import UsersRepository
from app.modules.auth.service import AuthService, requires_owner
from app.shared.constants import DEFAULT_LANG
from app.shared.database.operations import delete_all_db_data
from app.shared.i18n.messages import msg

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route("/user_dashboard", methods=["GET"])
def user_dashboard():
    
    return render_template('user_dashboard.html')


@auth_bp.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logout successful.")
    return redirect(url_for("main.home"))


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    # TODO: STUDY: CSRF, rate limiting, & lockout mechanisms

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with database_connection() as session:
            users_repo = UsersRepository(session)
            user = users_repo.get_user_by_username(username)
            
            if not user:
                flash(msg("username_nonexistent", DEFAULT_LANG))
                return redirect(url_for('auth.login'))
            elif not user.check_password(password):
                flash(msg("password_incorrect", DEFAULT_LANG))
                return redirect(url_for('auth.login'))
            else:
                remember = 'remember_user' in request.form
                login_user(user, remember=remember)  # Stores session data in persistent cookie, with expiration date, and cookie survives browser restarts
                return redirect(url_for('main.home'))

    else:
        return render_template('auth/login.html')
    

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('auth/register.html')
    
    elif request.method == "POST":
        form_data = request.form.to_dict()
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        name = form_data.get("name", "").strip()
        
        try:
            with database_connection() as session:
                auth_service = AuthService(session)
                user, errors = auth_service.register_user(
                    username=username, password=password, name=name, role=UserRole.USER
                )
                if errors:
                    for e in errors:
                        flash(e, "error")
                    return redirect(url_for("auth.register"))
                
        except Exception as e:
            print(f"DEBUG: Validation failed: {e}", file=sys.stderr)
            flash("hey")
            return redirect(url_for("auth.register"))
                    
        flash("Account successfully created!")
        return redirect(url_for("main.home"))



# Create & Seed only
@auth_bp.route('/init-demo', methods=["POST"])
def init_demo():
    # Boot logged in users first just in case
    try:
        logout_user()
    except Exception:
        pass

    with database_connection() as session:
        auth_service = AuthService(session)
        demo_user = auth_service.get_or_create_demo_user()
        login_user(demo_user)

    flash(msg("demo_ready", DEFAULT_LANG))
    return redirect(url_for('main.home'))

"""
Using multiple decorators! From BOTTOM to TOP:
1. @with_db_session - Wraps the function, injects the session
2. @requires_owner  - Wraps that result, checks role
3. @login_required     - Wraps that result, checks login
4. @auth_bp.route('/admin/reset-users', methods=["POST"]) - Wraps everything, handles HTTP routing

Bottom-up application order, top-down call order
"""
@auth_bp.route('/admin/reset-users', methods=["POST"])
@login_required
@requires_owner
@with_db_session
def reset_users(session): # <= @with_db_session injects session as 1st parameter, so we need to pass it in here
    """Delete all data + users, then create fresh demo + owner users."""
    logout_user()

    delete_all_db_data(session, include_users=True, reset_sequences=True)
    auth_service = AuthService(session)
    demo_user = auth_service.get_or_create_demo_user()
    owner_user = auth_service.get_or_create_owner_user()

    flash(msg("db_reset_users", DEFAULT_LANG))
    return redirect(url_for('auth.login'))

# Wipe app data only; reset IDs for more predictable seeding
@auth_bp.route('/admin/reset-db', methods=["POST"])
@login_required
@requires_owner
@with_db_session
def reset_database(session):

    delete_all_db_data(session, include_users=False, reset_sequences=True)

    flash(msg("db_reset", DEFAULT_LANG))
    return redirect(url_for('main.home'))


@auth_bp.route('/admin/reset-dev', methods=["POST"])
@login_required
@requires_owner
@with_db_session
def reset_dev(session):

    logout_user()

    auth_service = AuthService(session)
    owner_user = auth_service.get_or_create_owner_user()

    flash(msg("db_reset_dev", DEFAULT_LANG))
    return redirect(url_for('main.home'))
