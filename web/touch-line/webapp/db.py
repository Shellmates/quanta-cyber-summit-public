import sqlite3
from functools import wraps

from flask import current_app, g, redirect, session, url_for
from werkzeug.security import generate_password_hash


SEED_POSTS = [
    {
        "title": "Derby Day: The Midfield Battle That Decided It",
        "body": "Aggressive pressing in central areas turned a tight first half into a clear second-half edge.",
    },
    {
        "title": "Why the 4-3-3 Press Worked This Weekend",
        "body": "The front three pressed in curved runs, forcing long balls and giving the back line easy recoveries.",
    },
    {
        "title": "Three January Signings That Fit the Squad",
        "body": "A ball-winning six, a fast right winger, and a reliable backup full-back should be top priorities.",
    },
]
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            bio TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    count = db.execute("SELECT COUNT(*) AS n FROM posts").fetchone()["n"]
    if count == 0:
        db.executemany(
            "INSERT INTO posts (title, body) VALUES (?, ?)",
            [(post["title"], post["body"]) for post in SEED_POSTS],
        )

    bot_username = (current_app.config.get("BOT_USERNAME") or "").strip()
    bot_password = current_app.config.get("BOT_PASSWORD") or ""
    bot_bio = current_app.config.get("BOT_BIO") or ""
    if bot_username and bot_password:
        existing_bot = db.execute(
            "SELECT id FROM users WHERE username = ?",
            (bot_username,),
        ).fetchone()
        bot_password_hash = generate_password_hash(bot_password)

        if existing_bot is None:
            db.execute(
                "INSERT INTO users (username, password_hash, bio) VALUES (?, ?, ?)",
                (bot_username, bot_password_hash, bot_bio),
            )
        else:
            db.execute(
                "UPDATE users SET password_hash = ?, bio = ? WHERE id = ?",
                (bot_password_hash, bot_bio, existing_bot["id"]),
            )

    db.commit()


def load_current_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is None:
        return

    user = get_db().execute(
        "SELECT id, username, bio, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if user is not None:
        g.user = dict(user)


def inject_user():
    return {"current_user": g.get("user")}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.get("user") is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def fetch_posts():
    rows = get_db().execute(
        "SELECT id, title, body, created_at FROM posts ORDER BY id"
    ).fetchall()
    return [dict(row) for row in rows]


def fetch_post(post_id: int):
    row = get_db().execute(
        "SELECT id, title, body, created_at FROM posts WHERE id = ?",
        (post_id,),
    ).fetchone()
    return dict(row) if row else None
