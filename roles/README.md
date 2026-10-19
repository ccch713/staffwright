# Ready-Made AI Staff — Role Packs

Installing is the start; a new AI hire needs a job description. These role packs are distilled from real small-business engagements (see [docs/playbooks.md](../docs/playbooks.md)) so a new team can go **install → pick a role → useful in under an hour** — no prompt-engineering degree required.

| Pack | Hires as | Best for | Headline workflows |
|---|---|---|---|
| [front-desk](front-desk/) | receptionist | clinics, dental, salons, studios | FAQ from the KB, appointment reminders & no-show reduction, missed-call text-back, review requests |
| [lead-follower](lead-follower/) | sales development rep | anyone living on inbound leads | instant first response, missed-call text-back, 0/1/3/7-day follow-up cadence, qualification handoff |
| [ecommerce-ops](ecommerce-ops/) | ops assistant | online shops of 1–10 people | customer-reply drafts, review responses, listing polish, daily digest |
| [listing-writer](listing-writer/) | real-estate assistant | agencies & independent agents | platform-ready listings, lead qualification, viewing scheduling, fair-housing guard |
| [office-admin](office-admin/) | chief-of-staff assistant | every office | daily digest, meeting notes → knowledge base, invoice triage, handbook Q&A |
| [librarian](librarian/) | knowledge curator | teams drowning in docs | ingestion intake, stale detection, retrieval health, gap report |

## Activate a role in 3 steps (~5 minutes)

1. **Feed it** — create its knowledge-base folder (`data/kb/<role>/`) and drop in the files listed in the pack's *Setup* section (price list, policy, FAQs — whatever it must know).
2. **Hire it** — paste the pack's persona block into the agent settings (DSH Settings → your agent profile) with that folder attached.
3. **Try it** — run the *Starter prompts* in the pack. Iterate on the KB, not on the prompt.

## About the scheduled routines

Each pack ends with a `routines.yaml` spec (reminder sweeps, digests, follow-up cadence). The routine runner ships in **v0.9** (see the [roadmap](../README.md#roadmap)); until then, trigger the tasks on demand in chat or wire them with your OS cron. The specs are written so the runner can adopt them without edits.

## Write your own

Copy any pack as a template: *Mission → Daily work → Guardrails → Setup → Starter prompts → routines*. Keep the **Guardrails** section — it's what makes a role trustworthy enough to leave alone.

*Built a role pack worth sharing? Open a PR or start a Discussion — good packs get linked here.*
