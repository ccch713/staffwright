# Deployment Playbooks

Three setups distilled from real small-business engagements (China pilots, 2026). They are the field tests behind the [role packs](../roles/) — and they are written honestly: the numbers below are **design targets and engagement facts**, not vanity metrics. Each playbook lists what to measure, so you can hold your own deployment to a number.

## 1. Dental clinic — the front desk that never forgets

- **Client profile**: single-location dental clinic; the front desk drowns in phone calls and walk-in questions.
- **Staff hired**: [`front-desk`](../roles/front-desk/) + [`librarian`](../roles/librarian/)
- **Stack**: one mini PC on the clinic LAN · DSH engine + Staffwright gateway · a DeepSeek API key · KB = service & price list, insurance FAQ, opening hours, cancellation policy.
- **Engagement facts**: scoped in a half-day requirements workshop; first-customer pricing deliberately low in exchange for a documented, measurable case.
- **Design targets**: reminder coverage = 100% of bookings (day-before + morning-of); FAQ deflection ≥ 60% of desk interruptions; no-show rate tracked weekly — industry reports put proactive AI reminders at up to ~40% no-show reduction, and that's the bar.
- **Measure**: no-show %, desk interruptions/day, minutes to answer a price question.

## 2. E-commerce shop — ops without four dashboards

- **Client profile**: online shop run by 1–10 people; customer threads scattered across portals and chat apps.
- **Staff hired**: [`ecommerce-ops`](../roles/ecommerce-ops/) (+ [`lead-follower`](../roles/lead-follower/) for pre-sale inquiries)
- **Design targets**: first-response time < 5 min during staffed hours; 100% of public reviews answered within 24 h; the owner starts the day from one digest, not four dashboards.
- **Measure**: first-response time, review SLA, and — the number that must stay at zero — refund/payment errors (drafts are human-approved; the assistant never touches money).
- **Note from the field**: agree the acceptance numbers *before* deployment and put them in the contract. Automation without an acceptance number is where SMB AI projects die — this lesson is baked into Staffwright's audit-friendly reporting roadmap.

## 3. Real-estate agency — listings and leads on rails

- **Client profile**: small agency; agents write listings at night and lose portal leads in the message scramble.
- **Staff hired**: [`listing-writer`](../roles/listing-writer/) + [`lead-follower`](../roles/lead-follower/)
- **Design targets**: listing turnaround from "one evening" → 15 minutes per property; 100% of inquiries answered < 5 min with qualification captured; zero fair-housing phrasing flags.
- **Measure**: listing turnaround time, lead first-response time, flagged-listing count (target: 0).

## The pattern (why these three work)

1. **One workflow first** — "phones" or "leads", never both on day one. Broad adoption fails; single workflows stick.
2. **The KB is the product** — every playbook is 80% "which files the staff must know". Prompt quality is downstream of KB quality.
3. **Acceptance numbers in the contract** — a deployment is done when the number is met, not when the software is installed.

*Running one of these playbooks? We'd love to link your write-up here — open a PR or start a Discussion.*
