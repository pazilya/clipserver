# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A cross-device clipboard sharing server designed to run on a Raspberry Pi Zero, accessible over Tailscale. Devices (laptop, mobile) can push and pull clipboard text via HTTP. The Pi acts as the central clipboard store.

## Architecture

- **`app.py`** — Flask server exposing three endpoints:
  - `GET /` — Web UI (mobile-friendly, dark-themed, inline HTML/CSS/JS via `render_template_string`)
  - `GET /clip` — Returns current clipboard as plain text
  - `POST /clip` — Stores new clipboard text (body is raw `text/plain`)
  - Clipboard is persisted to `clipboard.txt`; push history is appended to `history.json`

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

## Key Notes

- The Pi is assumed to be reachable at hostname `pizero` over Tailscale on port 5000.
- The web UI is a single inline HTML string in `app.py` — no template files or static assets.
- `history.json` is append-only; `clipboard.txt` holds only the latest entry.
- `clip_aliases.sh` defaults to Wayland (`wl-copy`); for X11 environments swap in `xclip`.
