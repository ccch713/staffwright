#!/bin/bash
# Staffwright · one-command install & start script
# Usage: bash install.sh [--port 8500] [--no-test] [--bg]
# Works on: macOS 14+ / Ubuntu 22+ (Python 3.11+ or Docker)
set -euo pipefail

PORT=${DDW_PORT:-8500}
RUN_TESTS=true
BG_MODE=false
USE_DOCKER=false
WITH_DSH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --port) PORT=$2; shift 2;;
        --docker) USE_DOCKER=true; shift;;
        --with-dsh) WITH_DSH=true; shift;;
        --no-test) RUN_TESTS=false; shift;;
        --bg) BG_MODE=true; shift;;
        -h|--help)
            echo "Staffwright one-command install & start"
            echo "Usage: bash install.sh [options]"
            echo "  --port PORT   service port (default 8500)"
            echo "  --docker      deploy via Docker Compose (recommended for a fresh server)"
            echo "  --with-dsh    install the dsh workbench plugin (@deepddw/dsh-workbench) + MCP bridge into the dsh web profile"
            echo "  --no-test     skip the test suite"
            echo "  --bg          run in the background (non-docker mode)"
            exit 0;;
        *) echo "Unknown option: $1"; exit 1;;
    esac
done

log() { echo "[$(date '+%H:%M:%S')] $*"; }

if [ "$USE_DOCKER" = true ]; then
    log "Deploying via Docker Compose..."
    if [ ! -f .env ]; then
        cp .env.example .env
        log "Created .env — edit it and set DDW_ACCESS_TOKEN, then run this again"
        exit 0
    fi
    docker compose -f deepddw-compose.yml up -d --build
    log "Staffwright is up: http://localhost:8500/"
    exit 0
fi

# ---- Local venv path ----
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" &>/dev/null; then
        PYTHON="$candidate"; break
    fi
done
[ -n "$PYTHON" ] || { log "Python 3.11+ is required"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    log "Creating virtual environment..."
    $PYTHON -m venv .venv
fi
. .venv/bin/activate

if ! python -c "import fastapi, mcp" 2>/dev/null; then
    log "Installing dependencies..."
    pip install -q -r requirements.txt
fi

mkdir -p data logs

if [ "$RUN_TESTS" = true ] && [ -d "tests" ]; then
    log "Running tests..."
    python -m pytest tests/ plugins/ -q --no-header -p no:cacheprovider || log "Some tests did not pass (starting anyway — see output above)"
fi

if [ ! -f .env ] && [ -z "${DDW_ACCESS_TOKEN:-}" ]; then
    log "⚠️  DDW_ACCESS_TOKEN is not set — a development default token will be used (set a real one in production!)"
fi

# ---- dsh workbench plugin (v2.0: stock dsh UI + Staffwright capability injection) ----
# Configures the official dsh MCP bridge (knowledge base / memory / docs exposed to the stock
# dsh UI via the standard MCP interface). Requires dsh installed locally (npm i -g @deepseek-ai/dsh).
# Takes effect after restarting dsh web.
# v2.1 (2026-08-16): dropped the custom UI-plugin approach (it polluted the stock dsh UI) — pure official MCP.
if [ "$WITH_DSH" = true ]; then
    log "Configuring the dsh MCP bridge (Staffwright tools via the official interface)..."
    DSH_BIN="$(command -v dsh || true)"
    if [ -z "$DSH_BIN" ]; then
        log "⚠️  dsh command not found — skipping MCP configuration (you can run the dsh plugin commands manually)"
    else
        # 1) Make sure the mcp-client package is present in the web profile (the patch references it;
        #    if missing, this is skipped silently)
        if ! ls "$HOME/.dsh/profiles/web/node_modules/@deepseek-ai/dsh-mcp-client" >/dev/null 2>&1; then
            (cd "$HOME/.dsh/profiles/web" && pnpm add "@deepseek-ai/dsh-mcp-client@0.1.0-rc.6" >/dev/null 2>&1) \
                && log "mcp-client package installed" || log "⚠️  mcp-client install failed — the MCP bridge may not take effect"
        fi
        # 2) Append the MCP bridge config to the profile patch (5 tools; connects directly on LAN)
        PATCH_FILE="$HOME/.dsh/profiles/web/cordis.patch.yml"
        if [ -f "$PATCH_FILE" ] && ! grep -q "mcp-deepddw" "$PATCH_FILE" 2>/dev/null; then
            # The template ships with an empty "[]" placeholder line: it must be removed before
            # appending "- insert", otherwise the YAML is invalid
            if grep -q "^\[\]$" "$PATCH_FILE" 2>/dev/null; then
                sed -i '' '/^\[\]$/d' "$PATCH_FILE"
                log "Removed the empty-array placeholder line from the patch template (keeps YAML valid)"
            fi
            cat >> "$PATCH_FILE" <<'MCPEOF'
- insert:
    - id: mcp-deepddw
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: deepddw
        transport: streamable-http
        url: http://127.0.0.1:8600/api/v1/mcp
        headers: {}
MCPEOF
            log "MCP bridge written to $PATCH_FILE (takes effect after restarting dsh web)"
        fi
        log "Done: after restarting dsh web (dsh web), the Staffwright tools (knowledge base / memory / docs) appear in the dsh chat tool list via official MCP"
    fi
fi

log "Starting Staffwright (port $PORT)..."
# Optional TLS — when config/deployment.yaml sets security.tls.enabled=true, the
# ssl flags are added automatically (certificates come from ./scripts/gen_self_signed_cert.sh).
UVICORN_SSL_ARGS=""
if python -c "import yaml,sys; c=yaml.safe_load(open('config/deployment.yaml')) if __import__('os').path.exists('config/deployment.yaml') else {}; print('1' if (c.get('security',{}).get('tls',{}) or {}).get('enabled') else '0')" 2>/dev/null | grep -q 1; then
  CERT="$(python -c "import yaml,os; c=yaml.safe_load(open('config/deployment.yaml')); t=(c.get('security',{}).get('tls',{}) or {}); print(t.get('cert_file','./data/tls/cert.pem'))" 2>/dev/null)"
  KEY="$(python -c "import yaml,os; c=yaml.safe_load(open('config/deployment.yaml')); t=(c.get('security',{}).get('tls',{}) or {}); print(t.get('key_file','./data/tls/key.pem'))" 2>/dev/null)"
  if [ -f "$CERT" ] && [ -f "$KEY" ]; then
    UVICORN_SSL_ARGS="--ssl-certfile $CERT --ssl-keyfile $KEY"
    log "TLS enabled ($CERT) → https://<host>:$PORT"
  else
    log "Warning: security.tls.enabled=true but certificates are missing — run ./scripts/gen_self_signed_cert.sh first"
  fi
fi
if [ "$BG_MODE" = true ]; then
    # shellcheck disable=SC2086  # UVICORN_SSL_ARGS is intentionally word-split
    nohup python -m uvicorn core.main:app --host 0.0.0.0 --port "$PORT" $UVICORN_SSL_ARGS > logs/deepddw.log 2>&1 &
    echo $! > .deepddw.pid
    sleep 2
    log "Started in background: PID=$(cat .deepddw.pid), log at logs/deepddw.log"
else
    # shellcheck disable=SC2086
    python -m uvicorn core.main:app --host 0.0.0.0 --port "$PORT" $UVICORN_SSL_ARGS
fi
