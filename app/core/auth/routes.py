from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.core.database import database_connection
from app.core.auth.auth_utils import validate_username, validate_password, validate_name
from app.core.auth.models import User
from flask_login import login_user
from app.core.messages import MESSAGES

lang = "en"

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=["GET", "POST"])
def register():

    # TODO: Pull lang from a user's setting instead of hardcoding here?
    # Unsure whether to make it a user setting or a cookie via lang toggle
    lang = "en"
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
                validate_username(username, session, lang)
                + validate_password(password, lang)
                + validate_name(name, lang)
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

                session.add(user)
                session.flush()   # hits DB so user.id is populated
                
                login_user(user) # now user.id exists for the session
                flash(msg("register_success", lang, name=name))
                return redirect(url_for("main.dashboard"))

    else:
        return render_template('auth/register.html')