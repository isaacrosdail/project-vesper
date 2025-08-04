from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.core.database import database_connection
from app.core.auth.auth_utils import validate_username, validate_password, validate_name
from app.core.auth.models import User
from flask_login import login_user, login_required, logout_user
from app.core.messages import msg
from app.core.constants import DEFAULT_LANG
from app.core.auth.repository import get_user_by_username
import sys


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
    # TODO: CSRF, rate limiting, & lockout mechanisms

    if request.method == "POST":
        # Get form data: need username and password entry
        username = request.form.get("username")
        password = request.form.get("password")

        # 
        with database_connection() as session:
            user = get_user_by_username(username, session)
            
            if not user:
                flash(msg("username_nonexistent", DEFAULT_LANG))
            elif not user.check_password(password):
                flash(msg("password_incorrect", DEFAULT_LANG))
            else:
                remember = 'remember_user' in request.form
                login_user(user, remember=remember)  # Stores session data in persistent cookie, with expiration date, and cookie survives browser restarts
                return redirect(url_for('main.home'))

    else:
        return render_template('auth/login.html')
    

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    try:
        # TODO: Pull lang from a user's setting instead of hardcoding here
        # Unsure whether to make it a user setting or a cookie via lang toggle
        if request.method == "POST":
            # User types in creds, hits Submit.
            # 1. Grab form data
            form_data = request.form.to_dict()
            username = form_data.get("username")
            password = form_data.get("password")
            name = form_data.get("name").strip()

            with database_connection() as session:

                # Validate
                errors = (
                    validate_username(username, session, DEFAULT_LANG)
                    + validate_password(password, DEFAULT_LANG)
                    + validate_name(name, DEFAULT_LANG)
                )
                if errors:
                    for e in errors:
                        # Flash & redirect
                        flash(e, "error")
                    return redirect(url_for("auth.register"))
                else:
                    # Form data good => Proceed to hash & store user
                    user = User(username=username, name=name)
                    user.set_password(password) # instance method here hashes+salts
                    print(f"DEBUG: password_hash after set_password: {user.password_hash}", file=sys.stderr)
                    session.add(user)
                    session.flush()   # hits DB so user.id is populated
                    #login_user(user) # now user.id exists for the session
                    
                    try:
                        flash(msg("register_success", DEFAULT_LANG))
                    except Exception as flash_error:
                        print(f"FLASH ERROR: {flash_error}", file=sys.stderr)
                    return redirect(url_for("main.home"))

        else:
            return render_template('auth/register.html')
    except Exception as e:
        print(f"DEBUG: Validation failed: {e}", file=sys.stderr)
        flash("hey")
        return redirect(url_for("auth.register"))
