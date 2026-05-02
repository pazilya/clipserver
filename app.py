from flask import Flask, request, jsonify, render_template_string
import os
import json
from datetime import datetime

app = Flask(__name__)
CLIP_FILE = os.path.join(os.path.dirname(__file__), "clipboard.txt")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")

def append_history(text):
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    history.append({"text": text, "timestamp": datetime.utcnow().isoformat()})
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
    h1 {
      font-size: 1.3rem;
      font-weight: 600;
      color: #94a3b8;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 1.5rem;
    }
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
  <h1>📋 Clipboard</h1>

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
