# Clipboard Server Setup

## On the Pi

### 1. Copy files
```bash
mkdir ~/clipserver
# copy app.py and clipserver.service into ~/clipserver/
```

### 2. Install Flask
```bash
python3 -m venv ~/clipserver/venv
~/clipserver/venv/bin/pip install flask
```

### 3. Generate TLS certificate (Tailscale HTTPS)

The server runs over HTTPS using a Tailscale-issued Let's Encrypt cert.
Certs are stored in `~/clipserver/certs/` and are **gitignored** — you must
regenerate them on each fresh Pi install.

```bash
mkdir ~/clipserver/certs
sudo tailscale cert \
  --cert-file /home/pi/clipserver/certs/pizero.tailea2095.ts.net.crt \
  --key-file  /home/pi/clipserver/certs/pizero.tailea2095.ts.net.key \
  pizero.tailea2095.ts.net
```

> The cert is root-owned by default. The service unit handles this automatically
> with `ExecStartPre=+chown -R pi:pi /home/pi/clipserver/certs`, so you don't
> need to manually fix permissions. If you renew certs, the chown runs again on
> next service restart.
>
> Tailscale certs expire after ~90 days. Re-run the `tailscale cert` command to
> renew; then `sudo systemctl restart clipserver`.

### 4. Install as a systemd service (auto-start on boot)
```bash
sudo cp clipserver.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable clipserver
sudo systemctl start clipserver
```

### 5. Check it's running
```bash
sudo systemctl status clipserver
curl -s https://pizero.tailea2095.ts.net:5000/clip
```

---

## On your laptop

### 1. Add aliases to shell config
```bash
# bash
cat clip_aliases.sh >> ~/.bash_aliases && source ~/.bash_aliases

# zsh
cat clip_aliases.sh >> ~/.zshrc && source ~/.zshrc
```

### 2. Install a clipboard tool
```bash
sudo apt install wl-clipboard   # Wayland (preferred)
# or
sudo apt install xclip          # X11
```

`clip-pull` auto-detects whichever is installed.

### 3. Usage
```bash
clip-push "hello from laptop"
echo "piped text" | clip-push
clip-pull
```

---

## On mobile (any browser over Tailscale)

Open **https://pizero.tailea2095.ts.net:5000** in your browser.
- Paste text → Push
- Tap "Copy to device clipboard" to pull (requires HTTPS — already set up above)

### Tip: Add to home screen
In Safari or Chrome, use "Add to Home Screen" to make it feel like a native app.

---

## Quick test (from laptop)
```bash
clip-push "test from laptop"
# open https://pizero.tailea2095.ts.net:5000 on phone — should see "test from laptop"

# push from phone UI, then on laptop:
clip-pull
# should print and copy to your system clipboard
```

---

## History

Every push (via HTTP or directly on the Pi) is appended to `history.json`
alongside a UTC timestamp. This file is gitignored (runtime state).
