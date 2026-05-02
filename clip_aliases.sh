# Clipboard server aliases — works in both bash and zsh
# Source from ~/.bash_aliases (Pi) or ~/.zshrc (laptop)
#
# On pizero: reads/writes clipboard.txt and history.json directly (no HTTP)
# Elsewhere:  talks to the Pi over HTTP via Tailscale

_CLIP_FILE="/home/pi/clipserver/clipboard.txt"
_HIST_FILE="/home/pi/clipserver/history.json"
_CLIP_SERVER="http://pizero:5000"

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
