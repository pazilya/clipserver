# Clipboard Server Setup

## On the Pi

### 1. Copy files
```bash
mkdir ~/clipserver
# copy app.py into ~/clipserver/app.py
```

### 2. Install Flask
```bash
pip3 install flask --break-system-packages
```

### 3. Install as a systemd service (auto-start on boot)
```bash
sudo cp clipserver.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable clipserver
sudo systemctl start clipserver
```

### 4. Check it's running
```bash
sudo systemctl status clipserver
curl http://localhost:5000/clip
```

---

## On your laptop

### 1. Add aliases to ~/.bash_aliases
```bash
cat clip_aliases.sh >> ~/.bash_aliases
source ~/.bash_aliases
```

### 2. Install xclip (for auto-copy to clipboard on pull)
```bash
sudo apt install xclip
```

### 3. Usage
```bash
clip-push "hello from laptop"
echo "piped text" | clip-push
clip-pull
```

---

## On mobile (Termius or any browser)

Open **http://pizero:5000** in your browser over Tailscale.
- Paste text → Push
- Tap "Copy to device clipboard" to pull

### Tip: Add to home screen
In Safari or Chrome, use "Add to Home Screen" to make it feel like a native app.

---

## Quick test (from laptop)
```bash
clip-push "test from laptop"
# open http://pizero:5000 on phone — should see "test from laptop"

# push from phone UI, then on laptop:
clip-pull
# should print and copy the text you pushed from mobile
```
