from flask import Blueprint, abort, render_template, request

from .db import fetch_post, fetch_posts

bp = Blueprint("posts", __name__)


@bp.get("/")
def index():
    return render_template(
        "index.html",
        posts=fetch_posts(),
        last_visited=request.cookies.get("last_visited_post"),
        cookies=dict(request.cookies),
    )


@bp.get("/posts/<int:post_id>")
def post_details(post_id: int):
    post = fetch_post(post_id)
    if post is None:
        abort(404)
    return render_template("post.html", post=post)


@bp.get("/report-blogs")
def report_blogs():
    return render_template("report_blogs.html", posts=fetch_posts())
