from flask import Flask, request, jsonify, render_template_string
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

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Clipboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1rem;
    }
    .topbar {
      width: 100%;
      max-width: 480px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.5rem;
    }
    h1 {
      font-size: 1.3rem;
      font-weight: 600;
      color: #94a3b8;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    a.nav-link {
      font-size: 0.85rem;
      color: #6366f1;
      text-decoration: none;
    }
    a.nav-link:hover { text-decoration: underline; }
    .card {
      background: #1e2130;
      border: 1px solid #2d3148;
      border-radius: 12px;
      padding: 1.25rem;
      width: 100%;
      max-width: 480px;
      margin-bottom: 1rem;
    }
    label {
      display: block;
      font-size: 0.75rem;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 0.5rem;
    }
    textarea {
      width: 100%;
      min-height: 130px;
      background: #0f1117;
      border: 1px solid #2d3148;
      border-radius: 8px;
      color: #e2e8f0;
      font-size: 1rem;
      padding: 0.75rem;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s;
    }
    textarea:focus { border-color: #6366f1; }
    button {
      width: 100%;
      padding: 0.85rem;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      margin-top: 0.75rem;
      transition: opacity 0.2s;
    }
    button:active { opacity: 0.75; }
    .btn-push { background: #6366f1; color: #fff; }
    .btn-copy { background: #1e2130; border: 1px solid #2d3148; color: #94a3b8; }
    .current-card { background: #1e2130; border: 1px solid #2d3148; border-radius: 12px; padding: 1.25rem; width: 100%; max-width: 480px; }
    .current-text {
      background: #0f1117;
      border: 1px solid #2d3148;
      border-radius: 8px;
      padding: 0.75rem;
      font-size: 0.95rem;
      color: #cbd5e1;
      word-break: break-word;
      white-space: pre-wrap;
      min-height: 60px;
    }
    .toast {
      position: fixed;
      bottom: 1.5rem;
      left: 50%;
      transform: translateX(-50%) translateY(80px);
      background: #22c55e;
      color: #fff;
      padding: 0.6rem 1.4rem;
      border-radius: 99px;
      font-weight: 600;
      font-size: 0.9rem;
      transition: transform 0.3s ease;
      pointer-events: none;
    }
    .toast.show { transform: translateX(-50%) translateY(0); }
  </style>
</head>
<body>
  <div class="topbar">
    <h1>📋 Clipboard</h1>
    <a class="nav-link" href="/history">History →</a>
  </div>

  <div class="card">
    <label>Push new text</label>
    <textarea id="pushText" placeholder="Paste something here..."></textarea>
    <button class="btn-push" onclick="pushClip()">Push</button>
  </div>

  <div class="current-card">
    <label>Current clipboard</label>
    <div class="current-text" id="currentText">{{ current }}</div>
    <button class="btn-copy" onclick="copyToClipboard()">Copy to device clipboard</button>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2000);
    }

    async function pushClip() {
      const text = document.getElementById('pushText').value;
      if (!text.trim()) return;
      const res = await fetch('/clip', { method: 'POST', body: text, headers: { 'Content-Type': 'text/plain' } });
      if (res.ok) {
        document.getElementById('currentText').textContent = text;
        document.getElementById('pushText').value = '';
        showToast('Pushed ✓');
      }
    }

    async function copyToClipboard() {
      const text = document.getElementById('currentText').textContent;
      try {
        await navigator.clipboard.writeText(text);
        showToast('Copied ✓');
      } catch {
        showToast('Copy failed — try manual select');
      }
    }
  </script>
</body>
</html>
"""

HISTORY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Clipboard History</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0f1117;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1rem;
    }
    .topbar {
      width: 100%;
      max-width: 480px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.5rem;
    }
    h1 {
      font-size: 1.3rem;
      font-weight: 600;
      color: #94a3b8;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }
    a.nav-link {
      font-size: 0.85rem;
      color: #6366f1;
      text-decoration: none;
    }
    a.nav-link:hover { text-decoration: underline; }
    .entry {
      background: #1e2130;
      border: 1px solid #2d3148;
      border-radius: 12px;
      padding: 1rem 1.25rem;
      width: 100%;
      max-width: 480px;
      margin-bottom: 0.75rem;
    }
    .entry-meta {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }
    .timestamp {
      font-size: 0.75rem;
      color: #64748b;
      flex: 1;
    }
    .badge {
      font-size: 0.65rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 0.15rem 0.5rem;
      border-radius: 99px;
    }
    .badge-http { background: #1e3a5f; color: #60a5fa; }
    .badge-pi   { background: #1a3028; color: #4ade80; }
    .entry-text {
      font-size: 0.9rem;
      color: #cbd5e1;
      white-space: pre-wrap;
      word-break: break-word;
      background: #0f1117;
      border: 1px solid #2d3148;
      border-radius: 6px;
      padding: 0.6rem 0.75rem;
      max-height: 120px;
      overflow-y: auto;
      margin-bottom: 0.6rem;
    }
    .btn-copy {
      background: #1e2130;
      border: 1px solid #2d3148;
      color: #94a3b8;
      padding: 0.45rem 0.9rem;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s;
      width: auto;
      margin-top: 0;
    }
    .btn-copy:active { opacity: 0.7; }
    .pagination {
      display: flex;
      gap: 1rem;
      align-items: center;
      margin-top: 0.5rem;
      margin-bottom: 1rem;
    }
    .pagination a {
      color: #6366f1;
      text-decoration: none;
      font-size: 0.9rem;
      padding: 0.4rem 0.8rem;
      border: 1px solid #2d3148;
      border-radius: 6px;
    }
    .pagination a:hover { background: #1e2130; }
    .page-info {
      color: #64748b;
      font-size: 0.85rem;
    }
    .empty {
      color: #64748b;
      font-size: 0.95rem;
      margin-top: 2rem;
    }
    .toast {
      position: fixed;
      bottom: 1.5rem;
      left: 50%;
      transform: translateX(-50%) translateY(80px);
      background: #22c55e;
      color: #fff;
      padding: 0.6rem 1.4rem;
      border-radius: 99px;
      font-weight: 600;
      font-size: 0.9rem;
      transition: transform 0.3s ease;
      pointer-events: none;
    }
    .toast.show { transform: translateX(-50%) translateY(0); }
  </style>
</head>
<body>
  <div class="topbar">
    <h1>History</h1>
    <a class="nav-link" href="/">← Clipboard</a>
  </div>

  {% if entries %}
    {% for entry in entries %}
    <div class="entry">
      <div class="entry-meta">
        <span class="timestamp">{{ entry.display_ts }}</span>
        {% if entry.source == 'pi-local' %}
          <span class="badge badge-pi">Pi</span>
        {% else %}
          <span class="badge badge-http">HTTP</span>
        {% endif %}
      </div>
      <div class="entry-text">{{ entry.text }}</div>
      <button class="btn-copy" onclick="copyEntry({{ entry.text | tojson }})">Copy</button>
    </div>
    {% endfor %}

    <div class="pagination">
      {% if page > 1 %}
        <a href="/history?page={{ page - 1 }}">← Prev</a>
      {% endif %}
      <span class="page-info">Page {{ page }} of {{ total_pages }}</span>
      {% if page < total_pages %}
        <a href="/history?page={{ page + 1 }}">Next →</a>
      {% endif %}
    </div>
  {% else %}
    <p class="empty">No history yet.</p>
  {% endif %}

  <div class="toast" id="toast"></div>

  <script>
    function showToast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2000);
    }
    function copyEntry(text) {
      navigator.clipboard.writeText(text).then(() => {
        showToast('Copied ✓');
      }).catch(() => {
        showToast('Copy failed');
      });
    }
  </script>
</body>
</html>
"""


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
    return render_template_string(HTML, current=read_clip())

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
    return render_template_string(HISTORY_HTML, entries=entries, page=page, total_pages=total_pages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context=(CERT_FILE, KEY_FILE))
