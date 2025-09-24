from flask import Blueprint, redirect, render_template, request, url_for

from flask_login import login_required, login_user, logout_user
from app.shared.middleware import set_toast
from app._infra.database import database_connection, with_db_session
from app.modules.auth.models import UserRole
from app.modules.auth.repository import UsersRepository
from app.modules.auth.service import AuthService, requires_owner
from app.shared.database.helpers import delete_all_db_data
from app.modules.auth.validators import validate_user


auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route("/user_dashboard", methods=["GET"])
def user_dashboard():
    return render_template('user_dashboard.html')


@auth_bp.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    set_toast('Logout successful', 'success')
    logout_user()
    return redirect(url_for("main.home"))


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        with database_connection() as session:
            users_repo = UsersRepository(session)
            user = users_repo.get_user_by_username(username)
            
            if not user or not user.check_password(password):
                set_toast('Invalid login credentials', 'error')
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
        
        with database_connection() as session:
            repo = UsersRepository(session)
            service = AuthService(repo)
            result = service.register_user_from_form(form_data)

        if not result["success"]:
            set_toast(result["message"], 'error')
            return redirect(url_for("auth.register"))
        
        set_toast('Account successfully created!', 'success')
        return redirect(url_for("main.home"))


# Create & Seed only
@auth_bp.route('/init-demo', methods=["POST"])
def init_demo():
    logout_user() # boot logged in users just in case

    with database_connection() as session:
        repo = UsersRepository(session)
        auth_service = AuthService(repo)
        demo_user = auth_service.get_or_create_demo_user()
        login_user(demo_user)

    set_toast('Welcome to the demo!', 'success')
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
    repo = UsersRepository(session)
    auth_service = AuthService(repo)
    demo_user = auth_service.get_or_create_demo_user()
    owner_user = auth_service.get_or_create_owner_user()

    set_toast('Users reset!', 'success')
    return redirect(url_for('auth.login'))

# Wipe app data only; reset IDs for more predictable seeding
@auth_bp.route('/admin/reset-db', methods=["POST"])
@login_required
@requires_owner
@with_db_session
def reset_database(session):

    delete_all_db_data(session, include_users=False, reset_sequences=True)

    set_toast('DB reset!', 'success')
    return redirect(url_for('main.home'))


@auth_bp.route('/admin/reset-dev', methods=["POST"])
@login_required
@requires_owner
@with_db_session
def reset_dev(session):

    logout_user()

    delete_all_db_data(session, include_users=True, reset_sequences=True)
    repo = UsersRepository(session)
    auth_service = AuthService(repo)
    owner_user = auth_service.get_or_create_owner_user()

    set_toast('DEV: DB reset!', 'success')
    return redirect(url_for('main.home'))
