#!/usr/bin/env bash
set -Eeuo pipefail

XPRA_DISPLAY="${XPRA_DISPLAY:-:100}"
XPRA_BIND_HOST="${XPRA_BIND_HOST:-127.0.0.1}"
XPRA_BIND_PORT="${XPRA_BIND_PORT:-14500}"
APP_CMD="${APP_CMD:-python /app/demo/main.py --ui pyqt}"
XPRA_LOG_FILE="${XPRA_LOG_FILE:-/tmp/xpra.log}"
APP_LOG_FILE="${APP_LOG_FILE:-/tmp/app.log}"

cleanup() {
  echo "[start.sh] shutting down"
  xpra stop "${XPRA_DISPLAY}" >/dev/null 2>&1 || true
}

trap cleanup SIGINT SIGTERM EXIT

mkdir -p /run/user/1000 /tmp/runtime-pyuser /run/xpra /tmp/.X11-unix
chmod 700 /run/user/1000 /tmp/runtime-pyuser /run/xpra || true
if ! chmod 1777 /tmp/.X11-unix 2>/dev/null; then
  echo "[start.sh] warning: could not chmod /tmp/.X11-unix (continuing)" >&2
fi

mkdir -p /tmp/nginx/client_body /tmp/nginx/proxy /tmp/nginx/fastcgi /tmp/nginx/uwsgi /tmp/nginx/scgi
touch "${APP_LOG_FILE}" "${XPRA_LOG_FILE}"

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/runtime-pyuser}"

echo "[start.sh] starting Xpra on ${XPRA_BIND_HOST}:${XPRA_BIND_PORT} display ${XPRA_DISPLAY}"

xpra start "${XPRA_DISPLAY}" \
  --bind-tcp="${XPRA_BIND_HOST}:${XPRA_BIND_PORT}" \
  --html=on \
  --daemon=no \
  --exit-with-children=yes \
  --start-child="/bin/bash -lc '${APP_CMD}'" \
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

  if ! kill -0 "$!" 2>/dev/null; then
    echo "[start.sh] Xpra exited early. Last log lines:" >&2
    tail -n 100 "${XPRA_LOG_FILE}" >&2 || true
    exit 1
  fi

  sleep 1
  if [ "$i" -eq 30 ]; then
    echo "[start.sh] Xpra failed to become ready. Last log lines:" >&2
    tail -n 100 "${XPRA_LOG_FILE}" >&2 || true
    exit 1
  fi
done

echo "[start.sh] starting nginx"

# Stream both logs to container stdout so `make deploy` always shows app/xpra output.
tail -n +1 -F "${XPRA_LOG_FILE}" "${APP_LOG_FILE}" &

exec nginx -e /dev/stderr -g 'daemon off;'