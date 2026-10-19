#!/bin/bash
# Staffwright server start/stop script
# Usage: bash start.sh [start|stop|restart|status]
# Data & logs: ~/staffwright/data/ ~/staffwright/logs/  (override with DEEPDDW_HOME)

DEEPDDW_HOME="${DEEPDDW_HOME:-$HOME/deepddw}"
PYTHON="${DDW_PYTHON:-$(command -v python3.11 || command -v python3)}"
PORT=8500

start() {
  if pgrep -f "uvicorn core.main:app" > /dev/null; then
    echo "Staffwright is already running (port $PORT)"
    return 0
  fi
  cd "$DEEPDDW_HOME"
  set -a; . ./.env; set +a
  # --timeout-keep-alive 75: the 5s default is too short — browser connection pools reuse
  # idle connections that were already closed and report "Load failed" intermittently.
  nohup "$PYTHON" -m uvicorn core.main:app --host 0.0.0.0 --port "$PORT" --timeout-keep-alive 75 > logs/deepddw.log 2>&1 &
  echo $! > .deepddw.pid
  sleep 5
  if curl -s http://127.0.0.1:$PORT/health > /dev/null; then
    echo "Staffwright started: http://127.0.0.1:$PORT/ (PID $(cat .deepddw.pid))"
  else
    echo "⚠️ Startup may have failed — check logs/deepddw.log"
  fi
}

stop() {
  if pgrep -f "uvicorn core.main:app" > /dev/null; then
    pkill -f "uvicorn core.main:app"
    echo "Staffwright stopped"
  else
    echo "Staffwright is not running"
  fi
}

status() {
  if pgrep -f "uvicorn core.main:app" > /dev/null; then
    echo "Running (PID $(pgrep -f 'uvicorn core.main:app' | head -1))"
    curl -s http://127.0.0.1:$PORT/health
    echo
  else
    echo "Not running"
  fi
}

case "${1:-status}" in
  start) start ;;
  stop) stop ;;
  restart) stop; sleep 2; start ;;
  status) status ;;
  *) echo "Usage: $0 [start|stop|restart|status]"; exit 1 ;;
esac
