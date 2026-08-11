from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from werkzeug.wrappers import Response


from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_user, logout_user
from pydantic import ValidationError

from app._infra.database import database_connection, with_db_session
from app.modules.auth.repository import UsersRepository
from app.modules.auth.schemas import UserRegister
from app.modules.auth.service import AuthService
from app.shared.decorators import typed_login_required
from app.shared.exceptions import ServiceError
from app.shared.utils import ToastType, set_toast

auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.post("/logout")
@typed_login_required
def logout() -> Response:
    set_toast("Logout successful", "", ToastType.SUCCESS)
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
            set_toast("Login failed", "Invalid username or password", ToastType.ERROR)
            return redirect(url_for("auth.login_form"))
        remember = "remember_user" in request.form
        login_user(user, remember=remember)
        return redirect(url_for("main.home"))


@auth_bp.get("/register")
def register_form() -> tuple[str, int]:
    return render_template("auth/register.html"), 200


@auth_bp.post("/register")
@with_db_session
def register(session: Session) -> Response:
    try:
        validated = UserRegister(**request.form.to_dict())
    except ValidationError as e:
        for error in e.errors():
            set_toast("Registration failed", error["msg"], ToastType.ERROR)
        return redirect(url_for("auth.register_form"))

    service = AuthService(session, user_repo=UsersRepository(session))
    try:
        user = service.register_user(validated)
    except ServiceError as e:
        set_toast("Registration failed", str(e), ToastType.ERROR)
        return redirect(url_for("auth.register_form"))

    set_toast("Account created", "", ToastType.SUCCESS)
    login_user(user)
    return redirect(url_for("main.home"))


# Create & Seed only
@auth_bp.post("/init-demo")
@with_db_session
def init_demo(session: Session) -> Response:
    logout_user()  # boot logged in users just in case

    auth_service = AuthService(session, user_repo=UsersRepository(session))
    login_user(auth_service.create_demo_user())
    set_toast("Welcome to the demo", "", ToastType.SUCCESS)
    return redirect(url_for("main.home"))
