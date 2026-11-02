"""v0.8.0 (virtual-office): Virtual Office status panel API (read-only aggregation).

Purpose:
- Aggregate the **real activity** of Staffwright subsystems (device heartbeats /
  chat / memory writes / knowledge-base ingests / LLM usage) into
  "virtual staff on-duty status" for the pixel office at ``/ui/office.html``.
- **view-only**: this module performs no writes, drives no tasks, and exposes no
  generated content — the only text it emits is fixed job titles and whitelisted
  count phrases (numbers/minutes). No document contents, memory values, or chat
  transcripts ever leave this module (compliance red line, same design as DDW staffview).

Virtual staff roster (fixed 8 seats, mapped 1:1 in the frontend):
- Al (gateway)   — device registration / online heartbeats
- Sam (chat)     — chat message volume (last 24h)
- Penny (memory) — memory_entries writes (last 24h)
- Bo (kb)        — kb_documents ingests (last 24h)
- Max (llm)      — llm_usage_records calls/failures (last 24h)
- Dee (distill)  — distillation tasks (lit only when recent, else standing by)
- Bea (backup)   — latest backup time in the backups directory
- Rae (relay)    — org_relay.db binding activity (last 24h)

Endpoints (token-gated, append-only for backward compatibility):
- GET /api/v1/office/state → {residents, digest, banner, meta}
"""

from __future__ import annotations

import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends

from core.api_response import ok
from core.security.token_gate import require_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["virtual-office"])

# Active window: no new event for this many seconds → staff falls back to idle (no fake "forever typing")
ACTIVE_WINDOW_S = 30 * 60
# Snapshot cache: pulls within the same second share one snapshot (saves scans when dashboard + embeds are open together)
_CACHE_TTL_S = 5
_cache: Dict[str, Any] = {"ts": 0.0, "data": None}


def _db_path() -> Path:
    from core.config import get_settings

    settings = get_settings()
    cfg = settings.databases.get("main", {})
    if cfg.get("engine") == "sqlite":
        return Path(cfg.get("path", "./data/ddw_main.db")).resolve()
    return Path("./data/ddw_main.db").resolve()


def _conn(path: Path | None = None) -> sqlite3.Connection:
    p = path or _db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p), timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _scalar(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> Any:
    """Scalar query; returns None if the table is missing or the query fails (the office page must not crash on missing tables)."""
    try:
        row = conn.execute(sql, args).fetchone()
        return row[0] if row else None
    except sqlite3.Error:
        return None


def _latest(conn: sqlite3.Connection, table: str, col: str) -> str | None:
    """Latest timestamp (text column, YYYY-MM-DD HH:MM:SS or ISO)."""
    return _scalar(conn, f"SELECT MAX({col}) FROM {table}")


def _parse_ts(v: Any) -> float | None:
    if not v:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(v)[: len(fmt) + 2], fmt).timestamp()
        except ValueError:
            continue
    return None


def _recent(conn: sqlite3.Connection, table: str, col: str, hours: float = 24) -> int:
    """Rows in the last N hours (fallback: total count when the time column is unparseable)."""
    try:
        row = conn.execute(
            f"SELECT {col}, COUNT(*) AS n FROM {table} "
            f"WHERE {col} >= datetime('now', ?)", (f"-{int(hours)} hours",)
        ).fetchone()
        if row and row["n"]:
            return int(row["n"])
    except sqlite3.Error:
        pass
    total = _scalar(conn, f"SELECT COUNT(*) FROM {table}")
    return int(total or 0)


def office_snapshot() -> Dict[str, Any]:
    """Aggregated snapshot: fixed roster + real activity counts → input for the frontend state machine."""
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _CACHE_TTL_S:
        return _cache["data"]

    conn = _conn()
    residents: Dict[str, Dict[str, Any]] = {}
    digest_top: list[Dict[str, Any]] = []
    digest_fails: list[Dict[str, Any]] = []
    banner: Dict[str, Any] | None = None
    meta: Dict[str, Any] = {}

    try:  # noqa: SIM105 — each block fails independently; missing tables/dbs must never crash the panel
        # —— Al, gateway doorman: devices online ——
        try:
            rows = conn.execute(
                "SELECT device_id, device_name, last_seen FROM devices ORDER BY last_seen DESC"
            ).fetchall()
            online = 0
            for r in rows:
                ts = _parse_ts(r["last_seen"])
                if ts and now - ts <= 60:
                    online += 1
            total_dev = len(rows)
            if online > 0:
                residents["gateway"] = {
                    "state": "working",
                    "note": f"{online} devices online",
                    "today": {"done": total_dev, "failed": 0},
                }
            else:
                residents["gateway"] = {"state": "idle", "note": "No devices online"}
            meta["devices_online"] = online
            meta["devices_total"] = total_dev
            if total_dev:
                digest_top.append({"name": "Al", "text": f"Greeted {total_dev} devices today, {online} online now"})
        except sqlite3.Error:
            residents["gateway"] = {"state": "away"}

        # —— Sam, chat reception: messages ——
        try:
            n_chat = _recent(conn, "chat_messages", "created_at", 24)
            last_chat = _parse_ts(_latest(conn, "chat_messages", "created_at"))
            busy = last_chat is not None and now - last_chat <= ACTIVE_WINDOW_S
            residents["chat"] = {
                "state": "working" if busy else ("sleeping" if n_chat == 0 else "idle"),
                "note": ("Message just arrived" if busy else (f"{n_chat} messages today" if n_chat else "Quiet day — no messages yet")),
                "today": {"done": n_chat, "failed": 0},
            }
            if n_chat:
                digest_top.append({"name": "Sam", "text": f"Handled {n_chat} chat messages today"})
        except sqlite3.Error:
            residents["chat"] = {"state": "away"}

        # —— Penny, memory butler: memory_entries ——
        try:
            n_mem = _recent(conn, "memory_entries", "updated_at", 24)
            last_mem = _parse_ts(_latest(conn, "memory_entries", "updated_at"))
            busy = last_mem is not None and now - last_mem <= ACTIVE_WINDOW_S
            residents["memory"] = {
                "state": "doc" if busy else "idle",
                "note": ("Taking notes" if busy else f"{conn.execute('SELECT COUNT(*) FROM memory_entries').fetchone()[0]} memories on file"),
                "today": {"done": n_mem, "failed": 0},
            }
            if n_mem:
                digest_top.append({"name": "Penny", "text": f"Filed {n_mem} memories today"})
        except sqlite3.Error:
            residents["memory"] = {"state": "away"}

        # —— Bo, librarian: kb_documents ——
        try:
            n_kb = _recent(conn, "kb_documents", "created_at", 24)
            total_kb = _scalar(conn, "SELECT COUNT(*) FROM kb_documents") or 0
            last_kb = _parse_ts(_latest(conn, "kb_documents", "created_at"))
            busy = last_kb is not None and now - last_kb <= ACTIVE_WINDOW_S
            residents["kb"] = {
                "state": "doc" if busy else "idle",
                "note": ("Shelving new documents" if busy else f"{total_kb} documents on the shelves"),
                "today": {"done": n_kb, "failed": 0},
            }
            if n_kb:
                digest_top.append({"name": "Bo", "text": f"Ingested {n_kb} documents today"})
        except sqlite3.Error:
            residents["kb"] = {"state": "away"}

        # —— Max, meter clerk: llm_usage_records ——
        try:
            n_llm = _recent(conn, "llm_usage_records", "created_at", 24)
            n_fail = 0
            try:
                row = conn.execute(
                    "SELECT COUNT(*) FROM llm_usage_records "
                    "WHERE created_at >= datetime('now','-24 hours') AND ok = 0"
                ).fetchone()
                n_fail = int(row[0] or 0)
            except sqlite3.Error:
                pass
            last_llm = _parse_ts(_latest(conn, "llm_usage_records", "created_at"))
            busy = last_llm is not None and now - last_llm <= ACTIVE_WINDOW_S
            residents["llm"] = {
                "state": "upset" if n_fail > 3 else ("working" if busy else "idle"),
                "note": ("Metering calls" if busy else f"{n_llm} calls today"),
                "today": {"done": n_llm, "failed": n_fail},
            }
            if n_llm:
                digest_top.append({"name": "Max", "text": f"{n_llm} LLM calls today" + (f", {n_fail} failed" if n_fail else "")})
            if n_fail:
                digest_fails.append({"name": "Max", "text": f"{n_fail} LLM calls failed in the last 24h"})
                banner = {"level": "bad", "count": n_fail, "text": "LLM calls failed (last 24h) — check the gateway logs"}
        except sqlite3.Error:
            residents["llm"] = {"state": "away"}

        # —— Dee / Bea / Rae: light probes ——
        residents["distill"] = {"state": "idle", "note": "Standing by"}
        try:
            bdir = _db_path().parent / "backups"
            if bdir.exists():
                backups = sorted(bdir.glob("*.db*"), key=lambda p: p.stat().st_mtime, reverse=True)
                if backups:
                    age_h = (now - backups[0].stat().st_mtime) / 3600
                    residents["backup"] = {
                        "state": "celebrating" if age_h < 1 else "idle",
                        "note": f"Last backup {int(age_h)}h ago",
                    }
                    digest_top.append({"name": "Bea", "text": f"Last backup: {backups[0].name[:32]} ({int(age_h)}h ago)"})
                else:
                    residents["backup"] = {"state": "upset", "note": "No backup yet"}
                    digest_fails.append({"name": "Bea", "text": "The backups directory is empty — no backup taken yet"})
            else:
                residents["backup"] = {"state": "idle", "note": "Standing by"}
        except OSError:
            residents["backup"] = {"state": "idle", "note": "Standing by"}

        try:
            relay_db = _db_path().parent / "org_relay.db"
            if relay_db.exists():
                rc = _conn(relay_db)
                try:
                    n_bind = _recent(rc, "org_bindings", "created_at", 24)
                except sqlite3.Error:
                    n_bind = 0
                finally:
                    rc.close()
                residents["relay"] = {
                    "state": "working" if n_bind else "idle",
                    "note": f"{n_bind} bindings today" if n_bind else "Relay standing by",
                }
            else:
                residents["relay"] = {"state": "idle", "note": "Not enabled"}
        except sqlite3.Error:
            residents["relay"] = {"state": "idle", "note": "Not enabled"}

        meta["generated_at"] = datetime.now().isoformat(timespec="seconds")
    finally:
        conn.close()

    data = {
        "residents": residents,
        "digest": {"top": digest_top[:5], "fails": digest_fails},
        "banner": banner,
        "meta": meta,
    }
    _cache["ts"], _cache["data"] = now, data
    return data


@router.get("/office/state")
async def office_state(_: Dict[str, Any] = Depends(require_access_token)):
    """Virtual Office status panel (read-only aggregation, token-gated)."""
    return ok(office_snapshot())
