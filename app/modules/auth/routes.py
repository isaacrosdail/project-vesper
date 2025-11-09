
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app._infra.database import database_connection, with_db_session
from app.modules.auth.models import UserLangEnum, UserRoleEnum
from app.modules.auth.repository import UsersRepository
from app.modules.auth.service import AuthService, requires_owner
from app.modules.auth.validators import validate_user
from app.shared.database.helpers import delete_all_db_data
from app.shared.middleware import set_toast
from app.shared.parsers import parse_user_form_data

auth_bp = Blueprint('auth', __name__, template_folder='templates')


# TODO: Implement
@auth_bp.route("/user_dashboard", methods=["GET"])
def user_dashboard() -> Any:
    return render_template('user_dashboard.html')


@auth_bp.route('/logout', methods=["GET", "POST"])
@login_required # type: ignore[misc]
def logout() -> Any:
    set_toast('Logout successful', 'success')
    logout_user()
    return redirect(url_for("main.home"))


@auth_bp.route('/login', methods=["GET", "POST"])
def login() -> Any:
    if request.method == "POST":
        parsed_data = parse_user_form_data(request.form.to_dict())

        with database_connection() as session:
            users_repo = UsersRepository(session)
            user = users_repo.get_user_by_username(parsed_data["username"])
            
            if not user or not user.check_password(parsed_data["password"]):
                set_toast('Invalid username or password', 'error')
                return redirect(url_for('auth.login'))
            else:
                remember = 'remember_user' in request.form
                login_user(user, remember=remember)
                return redirect(url_for('main.home'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=["GET", "POST"])
def register() -> Any:
    if request.method == "POST":
        form_data = request.form.to_dict()
        parsed_data = parse_user_form_data(form_data)
        typed_data, errors = validate_user(parsed_data)

        if errors:
            for field_errors in errors.values():
                for error in field_errors:
                    set_toast(error, 'error')
            return redirect(url_for('auth.register'))


        with database_connection() as session:
            repo = UsersRepository(session)
            service = AuthService(repo)
            result = service.register_user(
                username=typed_data["username"],
                password=typed_data["password"],
                name=typed_data.get("name"),
                role=UserRoleEnum.USER,
                lang=UserLangEnum.EN
            )

        if not result["success"]:
            set_toast(result["message"], 'error')
            return redirect(url_for("auth.register"))
        
        set_toast('Account successfully created!', 'success')
        return redirect(url_for("main.home"))

    return render_template('auth/register.html')


# Create & Seed only
@auth_bp.route('/init-demo', methods=["POST"])
def init_demo() -> Any:
    logout_user() # boot logged in users just in case

    with database_connection() as session:
        repo = UsersRepository(session)
        auth_service = AuthService(repo)
        demo_user = auth_service.get_or_create_template_user("demo")
        login_user(demo_user)

    set_toast('Welcome to the demo!', 'success')
    return redirect(url_for('main.home'))


# Create & Seed only
@auth_bp.route('/init-owner', methods=["POST"])
def init_owner() -> Any:
    logout_user() # boot logged in users just in case

    with database_connection() as session:
        repo = UsersRepository(session)
        auth_service = AuthService(repo)
        owner_user = auth_service.get_or_create_template_user("owner")
        login_user(owner_user)

    set_toast('Welcome to the demo (OWNER)!', 'success')
    return redirect(url_for('main.home'))


@auth_bp.route('/admin/reset-users', methods=["POST"])
@requires_owner
@with_db_session
def reset_users(session: 'Session') -> Any:
    logout_user()

    delete_all_db_data(session, include_users=True, reset_sequences=True)
    repo = UsersRepository(session)
    auth_service = AuthService(repo)
    demo_user = auth_service.get_or_create_template_user("demo")
    owner_user = auth_service.get_or_create_template_user("owner")

    set_toast('Users reset!', 'success')
    return redirect(url_for('auth.login'))

# Wipe app data only; reset IDs for more predictable seeding
@auth_bp.route('/admin/reset-db', methods=["POST"])
@requires_owner
@with_db_session
def reset_database(session: 'Session') -> Any:

    delete_all_db_data(session, include_users=False, reset_sequences=True)

    set_toast('DB reset!', 'success')
    return redirect(url_for('main.home'))


@auth_bp.route('/admin/reset-dev', methods=["POST"])
@requires_owner
@with_db_session
def reset_dev(session: 'Session') -> Any:

    logout_user()

    delete_all_db_data(session, include_users=True, reset_sequences=True)
    repo = UsersRepository(session)
    auth_service = AuthService(repo)
    owner_user = auth_service.get_or_create_template_user("owner")

    set_toast('DEV: DB reset!', 'success')
    return redirect(url_for('main.home'))
