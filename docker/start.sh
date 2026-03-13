#!/usr/bin/env bash
set -Eeuo pipefail

XPRA_DISPLAY="${XPRA_DISPLAY:-:100}"
XPRA_BIND_HOST="${XPRA_BIND_HOST:-127.0.0.1}"
XPRA_BIND_PORT="${XPRA_BIND_PORT:-14500}"
APP_CMD="${APP_CMD:-python /app/main.py --ui pyqt}"
XPRA_LOG_FILE="${XPRA_LOG_FILE:-/tmp/xpra.log}"

cleanup() {
  echo "[start.sh] shutting down"
  xpra stop "${XPRA_DISPLAY}" >/dev/null 2>&1 || true
}

trap cleanup SIGINT SIGTERM EXIT

mkdir -p /run/user/1000 /tmp/runtime-pyuser /run/xpra /tmp/.X11-unix
chmod 700 /run/user/1000 /tmp/runtime-pyuser /run/xpra || true
chmod 1777 /tmp/.X11-unix || true

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-pyuser}"

echo "[start.sh] starting Xpra on ${XPRA_BIND_HOST}:${XPRA_BIND_PORT} display ${XPRA_DISPLAY}"

xpra start "${XPRA_DISPLAY}" \
  --bind-tcp="${XPRA_BIND_HOST}:${XPRA_BIND_PORT}" \
  --html=on \
  --daemon=no \
  --exit-with-children=yes \
  --start-child="${APP_CMD}" \
  --pulseaudio=no \
  --notifications=no \
  --bell=no \
  --xsettings=no \
  --mdns=no \
  --dbus-launch=no \
  --dbus-control=no \
  >>"${XPRA_LOG_FILE}" 2>&1 &

for i in $(seq 1 30); do
  if curl -fsS "http://${XPRA_BIND_HOST}:${XPRA_BIND_PORT}/" >/dev/null 2>&1; then
    echo "[start.sh] Xpra is ready"
    break
  fi
  sleep 1
  if [ "$i" -eq 30 ]; then
    echo "[start.sh] Xpra failed to become ready" >&2
    exit 1
  fi
done

echo "[start.sh] starting nginx"
exec nginx -g 'daemon off;'