# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A cross-device clipboard sharing server designed to run on a Raspberry Pi Zero, accessible over Tailscale. Devices (laptop, mobile) can push and pull clipboard text via HTTP. The Pi acts as the central clipboard store.

## Architecture

- **`app.py`** — Flask server. Templates live in `templates/`, styles/scripts in `static/css`/`static/js` (dark-themed, mobile-friendly).
  - `GET /` — Push clipboard UI; also shows the current clipboard with a favorite toggle
  - `GET /clip` — Returns current clipboard as plain text
  - `POST /clip` — Stores new clipboard text (body is raw `text/plain`)
  - `GET /history` — Paginated history UI; favorited entries are sorted to the top
  - `GET /api/history` — JSON history, newest first (optional `limit`)
  - `DELETE /api/history/<index>` — Removes a history entry
  - `POST /api/history/<index>/favorite` — Toggles an entry's favorite/pin status
  - Clipboard is persisted to `clipboard.txt`; push history is appended to `history.json`, each entry carrying a `favorite` bool (missing on legacy entries = not favorited)

- **`clip_aliases.sh`** — Shell functions for the laptop client (`clip-push`, `clip-pull`). Uses `curl` to talk to `http://pizero:5000`. Uses `wl-copy` (Wayland) for auto-copy on pull.

- **`clipserver.service`** — systemd unit that runs `app.py` under the `pi` user using a venv at `/home/pi/clipserver/venv/`.

## Running the Server

```bash
# Install dependency (on the Pi)
pip3 install flask --break-system-packages

# Run directly
python app.py

# Or via systemd (auto-starts on boot)
sudo systemctl start clipserver
sudo systemctl status clipserver
```

## Deployment (Pi)

The service file expects:
- Python venv at `/home/pi/clipserver/venv/`
- `app.py` at `/home/pi/clipserver/app.py`
- Running as user `pi`

```bash
sudo cp clipserver.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable clipserver
sudo systemctl start clipserver
```

## Laptop Client Setup

```bash
cat clip_aliases.sh >> ~/.bash_aliases
source ~/.bash_aliases

# Install wl-clipboard (Wayland) or xclip (X11)
sudo apt install wl-clipboard  # or xclip

# Usage
clip-push "some text"
echo "piped text" | clip-push
clip-pull
```

## TLS Certificates

The Flask app reads its cert and key from `clipserver/certs/` (gitignored — not in this repo).

- **Source**: `tailscale cert` for the domain `pizero.tailea2095.ts.net`. This issues a Let's Encrypt certificate, valid 90 days.
- **Must run on the Pi itself** — Tailscale verifies node ownership before issuing, so this can't be done from another machine.
- **`renew-cert.sh`** — reads the current cert's expiry, requests a renewal via `tailscale cert --min-validity 720h` (writing `certs/pizero.tailea2095.ts.net.crt`/`.key`), then compares expiry before/after. If the cert actually changed, it restarts `clipserver.service` so the running server picks up the new cert, and logs the renewal.
- **Root crontab** on the Pi runs it daily:
  ```
  35 5 * * * /home/pi/clipserver/renew-cert.sh >> /home/pi/logs/cert-renew.log 2>&1
  ```
  Since `tailscale cert` only issues a new cert once within `--min-validity` of expiry, most daily runs are no-ops (no expiry change, no restart) — the 90-day cert only actually renews (and restarts the service) periodically.

## Key Notes

- The Pi is assumed to be reachable at hostname `pizero` over Tailscale on port 5000.
- `history.json` entries are never reordered on disk; favorite-first ordering is applied only when rendering `/history`. `clipboard.txt` holds only the latest entry.
- The home page's favorite toggle only appears when the current clipboard text matches the most recent history entry (i.e. it was pushed via `/clip`, not written some other way).
- `clip_aliases.sh` defaults to Wayland (`wl-copy`); for X11 environments swap in `xclip`.
