#!/usr/bin/env bash
set -euo pipefail

DOMAIN="pizero.tailea2095.ts.net"
CERT_DIR="/home/pi/clipserver/certs"
BEFORE=$(openssl x509 -in "$CERT_DIR/$DOMAIN.crt" -noout -enddate)

tailscale cert \
  --min-validity 720h \
  --cert-file "$CERT_DIR/$DOMAIN.crt" \
  --key-file  "$CERT_DIR/$DOMAIN.key" \
  "$DOMAIN" >/dev/null

AFTER=$(openssl x509 -in "$CERT_DIR/$DOMAIN.crt" -noout -enddate)

if [ "$BEFORE" != "$AFTER" ]; then
    echo "$(date -Iseconds) renewed: $AFTER"
    systemctl restart clipserver.service
    echo "$(date -Iseconds) clipserver restarted"
fi
