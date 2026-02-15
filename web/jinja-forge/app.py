"""
Jinja Forge - Web CTF challenge (medium difficulty).
SSTI with filter on the template body only; context variable values are not filtered.
The player must pass forbidden strings via the context (title, snippet, attr1, etc.)
and use |attr() in the template to reach __class__, __subclasses__, etc.
"""

import json
import os
import re
from flask import Flask, request, jsonify

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "shellmates{s7i_byp4ss_v1a_c0nt3xt_p0llut10n}")

# Forbidden keywords in the template *body* only (not in context values)
BLOCKLIST = re.compile(
    r"config|request|self|flag|open|eval|exec|"
    r"__class__|__globals__|__builtins__|__init__|"
    r"lipsum|cycler|namespace|get_flashed_messages|joiner|"
    r"popen|subprocess|os\.|file\(|\.read\s*\(|\.write\s*\(",
    re.IGNORECASE,
)


def is_template_blocked(template: str) -> bool:
    """Check if the template contains a blocklisted string."""
    return bool(BLOCKLIST.search(template))


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Jinja Forge</title></head>
    <body>
    <h1>Jinja Forge</h1>
    <p>Render your snippet with variables. Submit a template and a context (JSON).</p>
    <form method="POST" action="/render">
        <label>Template (Jinja2):<br/>
        <textarea name="template" rows="6" cols="80" placeholder="{{ title }} - {{ author }}">{{ title }} - {{ author }}</textarea></label><br/>
        <label>Context (JSON, e.g. {"title":"Hello","author":"you"}):<br/>
        <textarea name="context" rows="4" cols="80">{"title": "Hello", "author": "player", "snippet": ""}</textarea></label><br/>
        <button type="submit">Render</button>
    </form>
    </body>
    </html>
    """


@app.route("/render", methods=["POST"])
def render():
    template = request.form.get("template", "").strip()
    context_str = request.form.get("context", "{}").strip()

    if not template:
        return jsonify({"error": "Empty template."}), 400

    if is_template_blocked(template):
        return jsonify({"error": "Template contains forbidden patterns."}), 400

    try:
        context = json.loads(context_str)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON context: {e}"}), 400

    # We do not inject request/config: only the provided context is used
    try:
        from jinja2 import Template
        t = Template(template)
        out = t.render(**context)
    except Exception as e:
        return jsonify({"error": str(e), "rendered": None}), 400

    return jsonify({"rendered": out})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
