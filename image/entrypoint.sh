#!/bin/bash
set -e

# Track child PIDs for cleanup
PIDS=()

cleanup() {
    echo ""
    echo "Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    exit 0
}

trap cleanup SIGTERM SIGINT

echo "=========================================="
echo "  Browser CDP Environment"
echo "=========================================="

# Clean up stale locks from previous runs
echo "[0/5] Cleaning up stale locks..."
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null || true
rm -f /app/chrome_profile/SingletonLock 2>/dev/null || true
rm -f /app/chrome_profile/SingletonCookie 2>/dev/null || true
rm -f /app/chrome_profile/SingletonSocket 2>/dev/null || true

echo "[1/5] Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
PIDS+=($!)
sleep 2

echo "[2/5] Starting window manager..."
fluxbox &
PIDS+=($!)
sleep 1

echo "[3/5] Starting VNC server on port 5900..."
x11vnc -display :99 -forever -passwd "${VNC_PASSWORD}" -quiet -bg
sleep 1

echo "[4/5] Starting Chromium (Playwright) with CDP..."
# Find Playwright's Chromium - look for the actual executable
# Newer Playwright uses chrome-linux64/chrome, older uses chrome-linux/chrome
CHROMIUM_PATH=$(find /root/.cache/ms-playwright -type f -name "chrome" 2>/dev/null | grep -v crashpad | grep -v headless | head -1)
if [ -z "$CHROMIUM_PATH" ]; then
  CHROMIUM_PATH=$(find /root/.cache/ms-playwright -type f -name "chromium" 2>/dev/null | head -1)
fi
if [ -z "$CHROMIUM_PATH" ]; then
  echo "ERROR: Playwright Chromium not found!"
  echo "Available files in playwright cache:"
  find /root/.cache/ms-playwright -type f -name "chrom*" 2>/dev/null || echo "  (none)"
  exit 1
fi
echo "Using Chromium at: $CHROMIUM_PATH"

$CHROMIUM_PATH \
  --no-sandbox \
  --disable-setuid-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --remote-debugging-port=9223 \
  --remote-debugging-address=0.0.0.0 \
  --remote-allow-origins=* \
  --user-data-dir=/app/chrome_profile \
  --disable-background-networking \
  --disable-default-apps \
  --disable-sync \
  --disable-translate \
  --no-first-run \
  --disable-background-timer-throttling \
  --disable-renderer-backgrounding \
  --disable-backgrounding-occluded-windows \
  --window-size=1920,1080 &
PIDS+=($!)

echo ""
echo "Waiting for Chrome CDP..."
CDP_READY=false
for _i in {1..30}; do
  if curl -s http://localhost:9223/json/version > /dev/null 2>&1; then
    echo "Chrome CDP is ready on internal port 9223!"
    CDP_READY=true
    break
  fi
  sleep 1
done

if [ "$CDP_READY" = false ]; then
  echo "ERROR: Chrome CDP failed to start within 30 seconds"
  exit 1
fi

echo "[5/5] Starting socat proxy (0.0.0.0:9222 -> localhost:9223)..."
socat TCP-LISTEN:9222,fork,reuseaddr TCP:localhost:9223 &
PIDS+=($!)

echo ""
echo "=========================================="
echo "  Browser environment ready!"
echo "=========================================="
echo ""
echo "  CDP:  http://localhost:9222"
echo "  VNC:  vnc://<container-name>.orb.local:5900"
echo ""
echo "=========================================="
echo ""

# Wait for any child to exit (or signal)
wait
