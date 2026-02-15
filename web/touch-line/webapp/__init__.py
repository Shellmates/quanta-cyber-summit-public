import os
from pathlib import Path

from flask import Flask

from .api import bp as api_bp
from .auth import bp as auth_bp
from .db import close_db, init_db, inject_user, load_current_user
from .posts import bp as posts_bp


def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-blog-secret")
    app.config["FLAG"] = os.environ.get("FLAG", "flag{fake_flag}")
    app.config["BOT_BASE_URL"] = os.environ.get("BOT_BASE_URL", "http://localhost:4002")
    app.config["BOT_USERNAME"] = os.environ.get("BOT_USERNAME", "touchline_bot")
    app.config["BOT_PASSWORD"] = os.environ.get("BOT_PASSWORD", "touchline_bot_password")
    app.config["BOT_BIO"] = os.environ.get(
        "BOT_BIO",
        "",
    )

    try:
        app.config["BOT_TIMEOUT_MS"] = int(os.environ.get("BOT_TIMEOUT_MS", "5000"))
    except ValueError:
        app.config["BOT_TIMEOUT_MS"] = 5000

    default_db = Path(app.root_path).parent / "touchline.db"
    app.config["DATABASE"] = os.environ.get("DATABASE_PATH", str(default_db))

    app.register_blueprint(posts_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    app.teardown_appcontext(close_db)
    app.before_request(load_current_user)
    app.context_processor(inject_user)

    with app.app_context():
        init_db()

    return app
