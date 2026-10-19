# Changelog

All notable changes to Staffwright are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The project was previously distributed as *deepddw*; early entries live in the git history.

## [0.8.0] - 2026-10-18

### Added — Virtual office (view-only activity visualization)

- **`/ui/office.html`**: a pixel-art virtual office where every Staffwright subsystem appears as a staff member (gateway doorman, chat receptionist, memory butler, librarian, meter clerk, distiller, backup clerk, relay). Real activity drives the animations: device heartbeats, chat messages, memory writes, knowledge-base ingests, LLM usage, backup timestamps, organization bindings.
  - Render core `frontend/assets/virtual-office.js`: single file, zero dependencies, fully programmatic pixel drawing (no third-party images/fonts/audio, no copyright exposure); a built-in demo script doubles as screenshot/promo material.
  - `GET /api/v1/office/state` (token-gated): read-only aggregation with **view-only whitelisted exposure** — the response contains job titles and statistics phrases only; no document contents, memory values, or chat transcripts ever leave this endpoint. Missing tables/stores degrade gracefully to the standby state (never a 500).
  - Staff members with no new events for 30 minutes fall back to idle (no "forever typing" fakery); LLM failures >3 times raise a top banner alert.
- Launcher navigation adds a "Virtual Office" entry.

## Earlier releases (summary)

- **Multi-device on LAN** — device identity & online registry, live status panel, per-token/IP rate limiting, SQLite WAL + write-lock concurrency (20 concurrent writers verified)
- **Team features** — workspace isolation, cross-device session resume, team distillation, scope promote, incognito sessions, retrieval health
- **Ops** — one-click backup/restore with integrity validation, optional TLS, Docker one-command deploy (verified end-to-end), version/upgrade check, Windows exe packaging via CI
- **Retrieval** — session → document auto-ingest, hybrid vector search (SQLite FTS5/LIKE + LanceDB, RRF fusion), memory relevance ranking (layer weight × hits × freshness)
- **Organization binding** — optional `bindcode-v1` server plugin (HMAC-signed short-lived bind codes; member-level tokens for an OpenAI-compatible chat endpoint backed by your own LLM gateway)
- **LLM workflows** — daily reflection with style guides; consolidation skips logging when the conversation is judged valueless

Full history: `git log`.
