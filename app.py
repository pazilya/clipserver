from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIP_FILE = os.path.join(BASE_DIR, "clipboard.txt")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
CERT_FILE = os.path.join(BASE_DIR, "certs", "pizero.tailea2095.ts.net.crt")
KEY_FILE = os.path.join(BASE_DIR, "certs", "pizero.tailea2095.ts.net.key")
ICONS_DIR = os.path.join(BASE_DIR, "icons")
ICONS_DARK_DIR = os.path.join(ICONS_DIR, "dark")
ICONS_LIGHT_DIR = os.path.join(ICONS_DIR, "light")
PAGE_SIZE = 25
CENTRAL = ZoneInfo("America/Chicago")

def fmt_timestamp(ts_str):
    try:
        dt = datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
        return dt.astimezone(CENTRAL).strftime("%Y-%m-%d %H:%M CT")
    except Exception:
        return ts_str[:16]

def append_history(text):
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    history.append({
        "text": text,
        "timestamp": datetime.utcnow().isoformat(),
        "source": "http-post",
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

@app.route("/favicon.ico")
@app.route("/favicon.png")
@app.route("/favicon-dark.png")
def favicon_dark():
    return send_from_directory(ICONS_DARK_DIR, "clipboard_favicon_32.png", mimetype="image/png")

@app.route("/favicon-light.png")
def favicon_light():
    return send_from_directory(ICONS_LIGHT_DIR, "clipboard_favicon_32.png", mimetype="image/png")

@app.route("/icon-256.png")
@app.route("/icon-256-dark.png")
def icon_256_dark():
    return send_from_directory(ICONS_DARK_DIR, "clipboard_header_256.png", mimetype="image/png")

@app.route("/icon-256-light.png")
def icon_256_light():
    return send_from_directory(ICONS_LIGHT_DIR, "clipboard_header_256.png", mimetype="image/png")

def read_clip():
    try:
        with open(CLIP_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def write_clip(text):
    with open(CLIP_FILE, "w") as f:
        f.write(text)

@app.route("/")
def index():
    return render_template("index.html", current=read_clip())

@app.route("/clip", methods=["GET"])
def get_clip():
    return read_clip(), 200, {"Content-Type": "text/plain"}

@app.route("/clip", methods=["POST"])
def post_clip():
    text = request.get_data(as_text=True)
    write_clip(text)
    append_history(text)
    return "OK", 200

@app.route("/api/history")
def api_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    limit = request.args.get("limit", type=int)
    history = list(reversed(history))
    if limit is not None:
        history = history[:limit]
    return jsonify(history)

@app.route("/history")
def history_page():
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    history = list(reversed(history))
    total = len(history)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = request.args.get("page", 1, type=int)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PAGE_SIZE
    entries = history[start:start + PAGE_SIZE]
    for e in entries:
        e["display_ts"] = fmt_timestamp(e.get("timestamp", ""))
    return render_template("history.html", entries=entries, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context=(CERT_FILE, KEY_FILE))
