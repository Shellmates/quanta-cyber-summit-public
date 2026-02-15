from urllib.parse import urlparse

from flask import Blueprint, current_app, jsonify, request
from .db import get_db

bp = Blueprint("api", __name__, url_prefix="/api")

MAX_BOT_LINKS = 2


def _normalize_bot_links(raw_links):
    if not isinstance(raw_links, list):
        raise ValueError("links must be a JSON array")
    if not raw_links:
        raise ValueError("provide at least 1 link")
    if len(raw_links) > MAX_BOT_LINKS:
        raise ValueError("at most 2 links are allowed")

    base_url = current_app.config["BOT_BASE_URL"].rstrip("/")
    normalized = []

    for raw_link in raw_links:
        if not isinstance(raw_link, str) or not raw_link.strip():
            raise ValueError("each link must be a non-empty string")

        link_suffix = raw_link.strip()
        parsed_suffix = urlparse(link_suffix)

        if parsed_suffix.scheme or parsed_suffix.netloc:
            raise ValueError("links must be path suffixes only (for example: /posts/1)")
        if not link_suffix.startswith("/"):
            raise ValueError("links must start with '/'")

        full_url = f"{base_url}{link_suffix}"

        normalized.append(full_url)

    return normalized


def _run_bot_visit(links):
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is not installed") from exc

    timeout_ms = current_app.config["BOT_TIMEOUT_MS"]
    base_url = current_app.config["BOT_BASE_URL"].rstrip("/")
    parsed_base_url = urlparse(base_url)
    bot_username = (current_app.config.get("BOT_USERNAME") or "").strip()
    if not bot_username:
        raise RuntimeError("BOT_USERNAME is not configured")
    bot_user_row = get_db().execute(
        "SELECT id FROM users WHERE username = ?",
        (bot_username,),
    ).fetchone()
    if bot_user_row is None:
        raise RuntimeError("bot user is not provisioned")

    session_cookie_name = current_app.config.get("SESSION_COOKIE_NAME", "session")
    session_serializer = current_app.session_interface.get_signing_serializer(current_app)
    if session_serializer is None:
        raise RuntimeError("session serializer is unavailable")
    session_cookie_value = session_serializer.dumps(
        {"is_bot": True, "user_id": int(bot_user_row["id"])}
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context()

        try:
            context.add_cookies(
                [
                    {
                        "name": session_cookie_name,
                        "value": session_cookie_value,
                        "url": f"{base_url}/",
                        "secure": parsed_base_url.scheme == "https",
                    }
                ]
            )

            page = context.new_page()
            for link in links:
                page.goto(link, wait_until="load", timeout=timeout_ms)
                page.wait_for_timeout(500)
        except PlaywrightTimeoutError as exc:
            raise RuntimeError("bot visit timed out") from exc
        finally:
            context.close()
            browser.close()


@bp.post("/bot/visit")
def bot_visit():
    payload = request.get_json(silent=True) or {}

    try:
        links = _normalize_bot_links(payload.get("links", []))
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    try:
        _run_bot_visit(links)
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500

    return jsonify({"ok": True, "visited": links})


@bp.get("/track-last-visited")
def track_last_visited():
    args = request.args
    post_id = str(args.get("post_id", ""))
    cookie_name = str(args.get("name") or "last_visited_post").strip()
    cookie_value = str(args.get("value", post_id))
    cookie_path = str(args.get("path", "/")) or "/"
    cookie_domain = args.get("domain")
    cookie_secure = str(args.get("secure", "false")).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    cookie_httponly = str(args.get("httponly", "false")).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if cookie_domain == "":
        cookie_domain = None
    if not cookie_name:
        cookie_name = "last_visited_post"

    response = jsonify(
        {
            "ok": True,
            "cookie": cookie_name,
            "value": cookie_value,
            "settings": {
                "name": cookie_name,
                "value": cookie_value,
                "path": cookie_path,
                "domain": cookie_domain,
                "secure": cookie_secure,
                "httponly": cookie_httponly,
            },
        }
    )
    response.set_cookie(
        cookie_name,
        cookie_value,
        path=cookie_path,
        domain=cookie_domain,
        secure=cookie_secure,
        httponly=cookie_httponly,
    )
    return response



