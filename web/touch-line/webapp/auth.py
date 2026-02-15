from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, login_required

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    bio = (request.form.get("bio") or "").strip()

    if not username or not password:
        flash("Username and password are required.", "error")
        return render_template("register.html", username=username, bio=bio), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing is not None:
        flash("Username already exists.", "error")
        return render_template("register.html", username=username, bio=bio), 400

    cursor = db.execute(
        "INSERT INTO users (username, password_hash, bio) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), bio),
    )
    db.commit()

    session["user_id"] = cursor.lastrowid
    flash("Registration successful. You are now logged in.", "ok")
    return redirect(url_for("auth.profile"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    user = get_db().execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        flash("Invalid username or password.", "error")
        return render_template("login.html", username=username), 401

    session["user_id"] = user["id"]
    flash("Logged in successfully.", "ok")
    return redirect(url_for("auth.profile"))


@bp.post("/logout")
def logout():
    session.clear()
    flash("Logged out.", "ok")
    return redirect(url_for("posts.index"))


@bp.get("/profile")
@login_required
def profile():
    user_posts_viewed = request.cookies.get("last_visited_post")
    response = make_response(
        render_template(
            "profile.html",
            user=g.user,
            last_visited=user_posts_viewed,
        )
    )
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; connect-src *; "
        "script-src 'self' 'unsafe-eval' https://ajax.googleapis.com;"
    )
    return response


@bp.get("/flag")
def flag():
    if not session.get("is_bot"):
        return "Forbidden", 403

    return current_app.config["FLAG"]
