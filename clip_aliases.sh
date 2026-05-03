# Clipboard server aliases — works in both bash and zsh
# Source from ~/.bash_aliases (Pi) or ~/.zshrc (laptop)
#
# On pizero: reads/writes clipboard.txt and history.json directly (no HTTP)
# Elsewhere:  talks to the Pi over HTTP via Tailscale

_CLIP_FILE="/home/pi/clipserver/clipboard.txt"
_HIST_FILE="/home/pi/clipserver/history.json"
_CLIP_SERVER="https://pizero.tailea2095.ts.net:5000"

_on_pi() {
  [[ "$(hostname)" == "pizero" ]]
}

# Append an entry to history.json; reads text from stdin to handle any content safely
_pi_append_history() {
  python3 - "$_HIST_FILE" <<'PYEOF'
import sys, json
from datetime import datetime, timezone
path = sys.argv[1]
text = sys.stdin.read()
try:
    with open(path) as f:
        history = json.load(f)
except (FileNotFoundError, ValueError):
    history = []
history.append({
    "text": text,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "source": "pi-local",
})
with open(path, "w") as f:
    json.dump(history, f, indent=2)
PYEOF
}

# Push: pass text as argument(s) or pipe stdin
# Usage: clip-push "some text"
#        echo "some text" | clip-push
clip-push() {
  local text
  if [[ -t 0 ]] && [[ -n "$*" ]]; then
    text="$*"
  else
    text="$(cat)"
  fi

  if _on_pi; then
    printf '%s' "$text" > "$_CLIP_FILE"
    printf '%s' "$text" | _pi_append_history
    echo "Pushed (local)."
  else
    printf '%s' "$text" | curl -s -X POST "$_CLIP_SERVER/clip" \
      -H 'Content-Type: text/plain' --data-binary @- > /dev/null
    echo "Pushed."
  fi
}

# Pull: print current clipboard; on laptop also copies to system clipboard
# Usage: clip-pull
clip-pull() {
  local text
  if _on_pi; then
    text="$(<"$_CLIP_FILE")"
  else
    text="$(curl -s "$_CLIP_SERVER/clip")"
  fi

  echo "$text"

  if ! _on_pi; then
    if command -v wl-copy &>/dev/null; then
      printf '%s' "$text" | wl-copy
      echo "(copied to clipboard via wl-copy)"
    elif command -v xclip &>/dev/null; then
      printf '%s' "$text" | xclip -selection clipboard
      echo "(copied to clipboard via xclip)"
    else
      echo "(no clipboard tool found — install wl-clipboard or xclip)"
    fi
  fi
}

# History: list recent entries (newest first) or re-push entry N
# Usage: clip-history          (shows last 15)
#        clip-history N        (re-pushes entry N to current clipboard)
clip-history() {
  local raw

  if _on_pi; then
    raw="$(python3 - "$_HIST_FILE" <<'PYEOF'
import sys, json
try:
    with open(sys.argv[1]) as f:
        data = json.load(f)
except (FileNotFoundError, ValueError):
    data = []
print(json.dumps(list(reversed(data))))
PYEOF
)"
  else
    raw="$(curl -s "$_CLIP_SERVER/api/history")"
  fi

  if [[ -n "$1" ]] && [[ "$1" =~ ^[1-9][0-9]*$ ]]; then
    local text
    text="$(python3 -c '
import sys, json
try:
    data = json.loads(sys.stdin.read())
except ValueError:
    data = []
idx = int(sys.argv[1]) - 1
if 0 <= idx < len(data):
    sys.stdout.write(data[idx]["text"])
else:
    print("No entry " + sys.argv[1] + ".", file=sys.stderr)
    sys.exit(1)
' "$1" <<< "$raw")"
    [[ $? -ne 0 ]] && return 1
    printf '%s' "$text" | clip-push
    return
  fi

  python3 -c '
import sys, json
try:
    data = json.loads(sys.stdin.read())
except ValueError:
    data = []
if not data:
    print("(no history)")
else:
    for i, e in enumerate(data[:15], 1):
        ts = e.get("timestamp", "")[:16].replace("T", " ")
        text = e.get("text", "").replace("\n", "\u21b5")
        if len(text) > 72:
            text = text[:72] + "\u2026"
        print(f"{i:>3}  [{ts}]  {text}")
' <<< "$raw"
}
