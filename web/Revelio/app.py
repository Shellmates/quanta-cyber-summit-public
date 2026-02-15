import os
import queue
import threading
import uuid
from urllib.parse import urlencode

from flask import Flask, redirect, render_template, request
from lxml import etree
from playwright.sync_api import sync_playwright


app = Flask(__name__)

SUBMISSIONS = {}
JOB_QUEUE = queue.Queue()

BOT_BASE_URL = os.getenv("BOT_BASE_URL", "http://127.0.0.1:5000")
FLAG = os.getenv("FLAG", "SHELLMATES{fake_flag}")

XML_DATA = f"""<?xml version=\"1.0\"?>
<inventory>
    <knownspells>
        <item>
            <id>1</id>
            <name>lumos</name>
            <description>Light spell for dark halls</description>
        </item>
        <item>
            <id>2</id>
            <name>alohomora</name>
            <description>Unlock spell for closed doors</description>
        </item>
    </knownspells>
    <forbiddenspells>
        <item>
            <id>3</id>
            <name>chamber-secret</name>
            <description>{FLAG}</description>
        </item>
    </forbiddenspells>
</inventory>
"""


def bot_worker():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        while True:
            job_id = JOB_QUEUE.get()
            if job_id is None:
                JOB_QUEUE.task_done()
                break
            url = f"{BOT_BASE_URL}/view/{job_id}"
            page = None
            try:
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=10000)
                page.wait_for_timeout(1000)
            except Exception:
                pass
            finally:
                if page is not None:
                    try:
                        page.close()
                    except Exception:
                        pass
                JOB_QUEUE.task_done()
        browser.close()


_worker_thread = threading.Thread(target=bot_worker, daemon=True)
_worker_thread.start()

@app.get("/")
def index():
    return render_template("index.html")


@app.post("/submit")
def submit():
    text = request.form.get("text", "")
    sort = request.form.get("sort", "asc")
    submission_id = str(uuid.uuid4())
    SUBMISSIONS[submission_id] = {"text": text, "sort": sort}
    JOB_QUEUE.put(submission_id)
    return render_template("submitted.html", submission_id=submission_id)


@app.get("/view/<submission_id>")
def view(submission_id):
    submission = SUBMISSIONS.get(submission_id)
    if not submission:
        return render_template("view.html")
    if "text" not in request.args:
        sort = submission.get("sort", "asc")
        safe_sort = "desc" if sort == "desc" else "asc"
        query = urlencode({"text": submission.get("text", ""), "sort": safe_sort})
        return redirect(f"/view/{submission_id}?{query}")
    sort = submission.get("sort", "asc")
    safe_sort = "desc" if sort == "desc" else "asc"
    query = urlencode({"text": submission.get("text", ""), "sort": safe_sort})
    if "sort" not in request.args:
        return redirect(f"/view/{submission_id}?{query}")
    return render_template("view.html")


@app.get("/preview")
def preview():
    return render_template("view.html")

@app.get("/search")
def xpath_search():
    remote_addr = request.remote_addr
    if remote_addr not in ("127.0.0.1", "::1"):
        return "Not Found", 404
    query = request.args.get("q", "")
    xml_root = etree.fromstring(XML_DATA.encode("utf-8"))
    xpath_expr = f"//knownspells/item[contains(name, '{query}') or contains(description, '{query}')]"
    matches = xml_root.xpath(xpath_expr)
    if not matches:
        return "No matches"
    lines = []
    for item in matches:
        item_id = item.findtext("id", default="")
        name = item.findtext("name", default="")
        description = item.findtext("description", default="")
        lines.append(f"{item_id} | {name} | {description}")
    return "\n".join(lines)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
