from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from werkzeug.wrappers import Response


from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from pydantic import ValidationError

from app._infra.database import database_connection, with_db_session
from app.modules.auth.repository import UsersRepository
from app.modules.auth.schemas import UserRegister
from app.modules.auth.service import AuthService
from app.shared.database.helpers import delete_all_db_data
from app.shared.decorators import owner_required, typed_login_required
from app.shared.exceptions import ServiceError
from app.shared.utils import set_toast

auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.post("/logout")
@typed_login_required
def logout() -> Response:
    set_toast("Logout successful", "success")
    logout_user()
    return redirect(url_for("main.home"))


@auth_bp.get("/login")
def login_form() -> tuple[str, int]:
    return render_template("auth/login.html"), 200


@auth_bp.post("/login")
def login() -> Response:
    data = request.form.to_dict()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    with database_connection() as session:
        users_repo = UsersRepository(session)
        user = users_repo.get_user_by_username(username)

        if not user or not user.check_password(password):
            set_toast("Invalid username or password", "error")
            return redirect(url_for("auth.login_form"))
        remember = "remember_user" in request.form
        login_user(user, remember=remember)
        return redirect(url_for("main.home"))


@auth_bp.get("/register")
def register_form() -> tuple[str, int]:
    return render_template("auth/register.html"), 200


@auth_bp.post("/register")
def register() -> Response:
    try:
        validated = UserRegister(**request.form.to_dict())
    except ValidationError as e:
        for error in e.errors():
            set_toast(error["msg"], "error")
        return redirect(url_for("auth.register_form"))

    with database_connection() as session:
        service = AuthService(session, user_repo=UsersRepository(session))
        try:
            service.register_user(
                username=validated.username,
                password=validated.password,
                name=validated.name,
            )
        except ServiceError as e:
            set_toast(str(e), "error")
            return redirect(url_for("auth.register_form"))

    set_toast("Account successfully created!", "success")
    return redirect(url_for("main.home"))


# Create & Seed only
@auth_bp.post("/init-demo")
def init_demo() -> Response:
    logout_user()  # boot logged in users just in case

    with database_connection() as session:
        auth_service = AuthService(session, user_repo=UsersRepository(session))
        demo_user = auth_service.get_or_create_template_user("demo")
        login_user(demo_user)

    set_toast("Welcome to the demo!", "success")
    return redirect(url_for("main.home"))


# Create & Seed only
@auth_bp.post("/init-owner")
def init_owner() -> Response:
    logout_user()  # boot logged in users just in case

    with database_connection() as session:
        auth_service = AuthService(session, user_repo=UsersRepository(session))
        owner_user = auth_service.get_or_create_template_user("owner")
        login_user(owner_user)

    set_toast("Welcome to the demo (OWNER)!", "success")
    return redirect(url_for("main.home"))


@auth_bp.post("/admin/reset-users")
@owner_required
@with_db_session
def reset_users(session: Session) -> Response:
    logout_user()

    delete_all_db_data(session, include_users=True, reset_sequences=True)
    auth_service = AuthService(session, user_repo=UsersRepository(session))
    _ = auth_service.get_or_create_template_user("demo")
    _ = auth_service.get_or_create_template_user("owner")

    set_toast("Users reset!", "success")
    return redirect(url_for("auth.login"))


# Wipe app data only; reset IDs for more predictable seeding
@auth_bp.post("/admin/reset-db")
@owner_required
@with_db_session
def reset_database(session: Session) -> Response:
    delete_all_db_data(session, include_users=False, reset_sequences=True)

    set_toast("DB reset!", "success")
    return redirect(url_for("main.home"))


@auth_bp.post("/admin/reset-dev")
@owner_required
@with_db_session
def reset_dev(session: Session) -> Response:
    logout_user()

    delete_all_db_data(session, include_users=True, reset_sequences=True)
    auth_service = AuthService(session, user_repo=UsersRepository(session))
    _ = auth_service.get_or_create_template_user("owner")

    set_toast("DEV: DB reset!", "success")
    return redirect(url_for("main.home"))
