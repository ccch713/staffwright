# Staffwright — Your Small Team's AI Staff, Self-Hosted

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/ccch713/staffwright/actions/workflows/ci.yml/badge.svg)](https://github.com/ccch713/staffwright/actions/workflows/ci.yml)
[![Listed in awesome-deepseek-harness](https://img.shields.io/badge/awesome--deepseek--harness-Listed-blue)](https://github.com/0xsline/awesome-deepseek-harness#memory--knowledge)

**Staffwright turns one ordinary computer into your team's AI workstation: shared long-term memory, a company knowledge base, document search, and a live office view of your AI at work. Deploy once — every phone, laptop and tablet on your network reaches it from the browser. No app installs. Up to ~20 people. MIT-licensed.**

*(staff + wright, as in "playwright" — a maker of staff.)*

- 🧠 **Shared memory** — cross-session long-term memory, exposed through the official MCP interface and shared by the whole team
- 📚 **Knowledge base** — ingest and search your docs anytime: industry material, SOPs, research notes
- 🌐 **Every device on the network** — deploy once on one always-on machine; desktops, phones and tablets all connect from the browser
- 🏠 **Your hardware** — data stays on your server and never leaves your LAN
- 🖥️ **Virtual office** — a pixel-art, view-only visualization of your AI staff at work

Under the hood, Staffwright runs the official **DeepSeek Harness (DSH)** engine untouched — zero source changes, all integration through DSH's standard MCP interface. Staffwright is the standalone, international-first distribution of the deepDDW project; the DSH-plugin line continues at [ccch713/deepddw](https://github.com/ccch713/deepddw).

> ## ⚠️ Read Before Installing
>
> Staffwright implements **its own memory and knowledge-base isolation**. To avoid conflicts or memory confusion:
>
> 1. **Back up** your existing memory and knowledge-base contents (wherever they live in your DSH setup);
> 2. **Uninstall/disable** any other memory or knowledge-base plugins;
> 3. Only then install Staffwright and let it own the memory & knowledge-base stack.
>
> Running it alongside other memory/KB plugins may cause data conflicts or memory mixing between namespaces.

---

## Try It in 60 Seconds

```bash
# 1. On the always-on machine (macOS 14+ / Ubuntu 22+):
git clone https://github.com/ccch713/staffwright.git && cd staffwright
./install.sh --with-dsh        # installs the DSH engine automatically if missing,
                               # then the gateway + DSH MCP bridge
./install.sh --port 8600       # 2. start (runs the test suite first, then serves)

# 3. From any device on the same network:
#    http://<server-ip>:8600/   → the DSH workbench, team-wide
#    Phones/tablets: "Add to Home Screen" for an App-like experience

# 4. Add your API key in DSH Settings → Models (see "Do I need an API key?" below)
# 5. In chat, ask the model to "search the knowledge base" or "remember …"
#    → it auto-invokes the built-in MCP tools
```

**Requirements**: one ordinary computer/server (**8 GB RAM minimum, 16 GB+ recommended**), Python 3.11+, no GPU needed (LLM via cloud API or local Ollama).

## Do I Need an API Key?

Staffwright ships **no keys, no accounts, no lock-in** — you pick one of three ways to give your staff a brain. Nothing else needs configuring: the gateway, memory, knowledge base and document search work out of the box; the key only powers the chat model.

| Option | Cost | Best for |
|---|---|---|
| **DeepSeek cloud key** | A few dollars a month for a whole small team — DeepSeek's API is among the cheapest of frontier-grade models | Fastest start: paste one key in DSH Settings → Models |
| **Local Ollama** (or any OpenAI-compatible endpoint) | Free, offline | Privacy-max / air-gapped networks |
| **Managed relay** *(planned)* | Monthly bundle, zero config | "Just make it work" teams — opt-in, never a default |

Then hire your first staff member in ~5 minutes from [`roles/`](roles/) — see below.

**Prefer Docker?**

```bash
cp .env.example .env    # set DDW_ACCESS_TOKEN
docker compose -f deepddw-compose.yml up -d --build
# → http://<host>:8500/
```

### Windows (standalone exe)

A Windows build is produced automatically by CI — download `deepddw-windows.zip` (legacy artifact name) from the latest **Actions → Artifacts**:

```bash
deepddw-windows/deepddw.exe          # unzip anywhere, no Python/Node needed
# optional: set DDW_DATA_DIR / DDW_ACCESS_TOKEN
# starts on 0.0.0.0:8500 → open http://<host>:8500/health
```

Upgrades: replace the folder with a newer zip — your data (under `%USERPROFILE%\.deepddw`) is untouched. See `docs/windows-packaging.md`.

---

## Why Staffwright?

Most AI-assistant setups stop at "chat in a browser tab". Staffwright is a **complete workstation**:

| Typical self-hosted assistant | Staffwright |
|---|---|
| 🔒 Bound to one machine, or one browser profile | ✅ **LAN-wide access**: deploy once; every device on the network connects |
| 🧠 No memory between sessions | ✅ Long-term memory write/search — the assistant accumulates context |
| 📚 No knowledge base | ✅ Ingest & search your own docs, SOPs and notes, callable from chat |
| 👤 Single-user mindset | ✅ **Team mode**: multi-user accounts, team memory distillation, workspace isolation, incognito sessions, retrieval health |
| 🕶️ Opaque backend | ✅ **Virtual office**: watch every subsystem at work — view-only by design |

**In one sentence**: turn a "personal AI toy" into a tool a small team actually runs its daily AI workflow on — fully packaged, easy to deploy, low maintenance, up to ~20 people.

> **Rule of thumb**: one instance per team of ≤20 people on one network. If your scenario fits in one room, one floor, or one VPN, Staffwright fits you.

---

## What's Inside

| Capability | What you get |
|---|---|
| 🧠 Memory | Cross-session long-term memory; results ranked by relevance (layer weight × hit count × freshness) |
| 📚 Knowledge base | Ingest & search; session → document auto-ingest; hybrid retrieval (SQLite FTS5 + optional LanceDB vectors, RRF fusion) |
| 🔎 Document search | Optional SearXNG aggregate search service |
| 🌐 Multi-device gateway | Device identity & online registry, live status panel, rate limiting, session resume across devices |
| 👥 Team features | Multi-user accounts, team distillation (deduplicated shared team memory), workspace isolation, scope promote, incognito |
| 🔌 DSH integration | Official MCP interface (`streamable-http`) — DSH UI, settings and model config stay 100% official |
| 🖥️ Virtual office | Real-activity pixel-art visualization; failures raise a banner; day digest importance-weighted |
| 🛟 Ops | One-click backup/restore, optional TLS, Docker one-command deploy, version/upgrade check, Windows exe |

## Ready-Made AI Staff — Pick a Role, Not a Blank Prompt

Installing is not the finish line; a new AI hire needs a job description. Staffwright ships **role packs** distilled from real small-business deployments, so a new team goes *install → pick a role → useful in under an hour*:

| Role pack | Hires as | Headline workflows |
|---|---|---|
| [`front-desk`](roles/front-desk/) | receptionist | FAQ from KB, appointment reminders & no-show reduction, missed-call text-back, review requests |
| [`lead-follower`](roles/lead-follower/) | sales development rep | instant first response, missed-call text-back, 0/1/3/7-day follow-up cadence |
| [`ecommerce-ops`](roles/ecommerce-ops/) | ops assistant | customer-reply drafts, review responses, listing polish, daily digest |
| [`listing-writer`](roles/listing-writer/) | real-estate assistant | platform-ready listings, lead qualification, viewing scheduling |
| [`office-admin`](roles/office-admin/) | chief-of-staff assistant | daily digest, meeting notes → KB, invoice triage |
| [`librarian`](roles/librarian/) | knowledge curator | KB ingestion & curation, retrieval health, gap reports |

The field-tested deployments behind these packs — dental clinic, e-commerce shop, real-estate agency — are documented in [`docs/playbooks.md`](docs/playbooks.md).

---

## How It Works

```
📱 Phone / 💻 Desktop / 📱 Tablet / 🖥️ Laptop — any device on the network
   │                  (browser access, no app install)
   ▼
Staffwright Gateway (one server on your network)
   ├─ /dsh/*     proxy → DSH engine (official UI, model config & chat untouched)
   ├─ /api/*     proxy → DSH RPC/API
   └─ /api/v1/*  Staffwright capabilities: Knowledge Base / Memory / Docs / LLM config
        │
        │  DSH official MCP client (streamable-http)
        ▼
Staffwright MCP tools (auto-invoked by the model)
   ├─ mcp__deepddw__ddw_kb_search           knowledge base search
   ├─ mcp__deepddw__ddw_memory_put          write memory
   ├─ mcp__deepddw__ddw_memory_search       search memory
   └─ mcp__deepddw__ddw_docs_portal_search  document search
```

**Integration = DSH standard MCP** — zero intrusion, zero changes to DSH source. (Tool names keep the internal `deepddw` codename; a rename pass is on the roadmap.)

---

## Virtual Office

Open `/ui/office.html` and watch your Staffwright at work: every subsystem is a pixel-art staff member — the gateway doorman waves devices in, the chat receptionist types away, the memory butler files notes, the librarian shelves new docs, the meter clerk bills LLM calls. Real activity drives the animations (no fake loops: 30 minutes without events → back to idle); failures raise a banner; the day's digest is importance-weighted. Fully programmatic rendering — zero third-party art assets, zero runtime dependencies. **View-only by design**: the API exposes nothing but job titles and whitelisted count phrases — never document contents, memory values, or chat transcripts.

---

## Security & Privacy

| Capability | Description |
|-----------|-------------|
| 🔐 Local-only data | Knowledge base & memory stay on your server, never leave the network |
| 🏠 LAN password-free | Optional (opt-in): LAN requests skip the token — **OFF by default** (`DDW_LAN_BYPASS=1`; trusted LANs only) |
| 🌐 External access | Optional token gate (short-code supported); unauthorized → 401 |
| 🛡️ DSH secure binding | DSH stays bound to localhost; the gateway exposes it — official security design preserved |
| 🧾 Audit-friendly | View-only office API, whitelisted phrases only; backup/restore with validated integrity checks |

---

## Roadmap

Only items actually planned or already delivered are listed.

**Delivered highlights** (full history in git log):

- Multi-device on LAN — device registry, status panel, rate limiting, SQLite WAL concurrency (up to 20 devices, load-tested: P95 ≤ 126 ms, 0% errors)
- Workspace isolation · cross-device session resume · optional TLS · backup/restore API · version/upgrade check
- Docker one-command deployment (verified end-to-end) · Windows exe via CI
- Session → document auto-ingest · hybrid vector search · memory relevance ranking
- Organization binding (optional `bindcode-v1` plugin) — act as the enterprise backend for assistant apps; HMAC-signed short-lived bind codes; member tokens never touch the admin API
- Virtual office (view-only activity visualization)

**Planned:**

- [ ] Scheduled staff routines — cron-driven roles (watch this space)
- [ ] One-line `curl … | bash` installer
- [ ] Full English documentation pass (some docs/UI strings still reference the legacy `deepddw` codename)
- [ ] Managed cloud (overseas regions)
- [ ] Optional managed relay for model tokens — zero-config keys for teams who want them; strictly opt-in, BYO-key stays the default
- [ ] Community Discord

---

## Commercial & Support

**Staffwright is free and fully featured forever.** Open source is the product — there are no feature gates and no "Pro-only" paywalls in this repository.

Paid convenience tiers (managed cloud hosting, enterprise collaboration: SSO, audit logs, private-deployment support) are being prepared for international availability. In the meantime: questions, deployment help and enterprise inquiries → [GitHub Discussions](https://github.com/ccch713/staffwright/discussions) or open an issue.

---

## Community

- 💬 [Discussions](https://github.com/ccch713/staffwright/discussions) — questions, show & tell, deployment help
- 🐛 [Issues](https://github.com/ccch713/staffwright/issues) — bug reports & feature requests
- 🤝 Contributing: see [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

| Component | License |
|-----------|---------|
| Staffwright (gateway, memory, knowledge base, docs portal, office) | MIT |
| DeepSeek Harness (DSH engine, source untouched) | MIT |
| SearXNG (optional aggregate search) | AGPL-3.0 (server-side HTTP, exemption assessed) |

See [`NOTICE`](NOTICE) for full third-party attribution.
