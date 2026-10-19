# Security Policy & Third-Party Plugin Disclaimer

> Last updated: 2026-10-19

## Reporting a Vulnerability

Please use **GitHub private vulnerability reporting** (the "Security" tab of this repository) instead of opening a public issue. Include reproduction steps and affected versions. Reporters are credited in release notes unless they ask otherwise.

## Supported Versions

Security fixes target the **latest release** on the default branch only.

## Plugin Security Disclaimer

Staffwright integrates the **official DeepSeek Harness (DSH) plugin mechanism** — plugins are installed via DSH's official command (`dsh plugin --profile web add <npm-package>`) **from the official npm registry only**. This is the only channel we recommend, to minimize supply-chain poisoning risk.

Staffwright's data guarantees cover **the memory & knowledge-base stack only**: your documents and memory stay on your server; we do not steal, exploit, or sell data. We disclaim the supply chain of any third-party plugin you install beyond that.

## Scope & Guarantees

- Nothing in the core phones home beyond the optional version/upgrade check (1h cache, degrades gracefully offline).
- The virtual office API is **view-only by design**: it exposes nothing but job titles and whitelisted count phrases — never document contents, memory values, or chat transcripts.

## Deployment Hardening

- Set a long random `DDW_ACCESS_TOKEN` in production (a dev default is used only when unset, with a startup warning).
- `DDW_LAN_BYPASS` is **off by default** — keep it off unless your LAN is trusted.
- For access from outside your network, put a reverse proxy with TLS (Caddy/Nginx) in front; see `docs/tls.md`.
- The organization-binding plugin (`bindcode-v1`) is **off by default**; bind codes are HMAC-signed, short-lived, use-capped and revocable, and member-level tokens never unlock the admin API.
