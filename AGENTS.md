# Notes for Coding Agents & Contributors

Practical orientation for working in this repository.

- **Stack**: FastAPI gateway + SQLite (WAL) core; DSH engine integration exclusively via the standard MCP interface (`streamable-http`); frontend is static HTML under `frontend/`; tests use pytest (`tests/`, `plugins/`).
- **Run tests**: `python -m pytest tests/ plugins/ -q`
- **Entry point**: `core/main.py` · runtime config: `config/deployment.yaml` · environment template: `.env.example`
- **Deployment paths**: `./install.sh` (venv) or `docker compose -f deepddw-compose.yml up -d --build`
- **Constraints**:
  - Never commit secrets — `.env` is gitignored, and CI should stay green (`pytest` + `ruff`).
  - Keep the DSH source untouched; all integration goes through its official MCP/plugin mechanisms.
  - Schema changes to memory/knowledge-base storage must ship backward-compatible migrations; backup/restore must keep validating integrity.
  - The view-only guarantee of the virtual office API is a hard boundary: never expose document contents, memory values, or chat transcripts through it.
- **Legacy codename**: internals may still reference `deepddw` (tool names, container names, log paths). Renaming is planned; until then keep new user-facing copy on the Staffwright brand and do not mix the two names in the same sentence.
