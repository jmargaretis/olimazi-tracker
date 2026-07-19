# SOL work packet — active

**Packet:** tracker-#7 · issued 2026-07-19 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`; report in the required REPORT.md format.

**Packet tracker-#6 (whole-dollar, grand total, ALERTS): ACCEPTED** — commit 433a19c.
Note: John reordered the queue — this Management page ships BEFORE the client
organizer packets A & B.

## Packet tracker-#7 scope — Property Management page (page 3) + product rename

A third page alongside the reconciliation dashboard: operational management of the
rental — tenant issues, work/repair tracking, and lease/insurance documents.

### 0. Product rename (added 2026-07-19, John's call)
Rename the user-facing product title everywhere it renders:
- Dashboard, management page, and report titles: **"Rental Manager"** as the main
  title with **"Sch. E"** as smaller subtext beneath/beside it (e.g. an h1 with a
  muted smaller-font span). Replace title-position uses of "Schedule E" /
  "Sch. E Dashboard" accordingly. Keep tax-line references in the BODY (e.g.
  "Schedule E line 14") unchanged — the rename is branding, not terminology.
- `docs/SETUP.md`: update the page-title promise ("a page titled **Schedule E**"
  → "a page titled **Rental Manager**") and any other title references.
- Naming convention for the future (record in README or a comment, no code):
  the Sch. C counterpart, when built, is titled **"Business Manager"** with
  "Sch. C" subtext. Nothing to build for Sch. C in this packet.
- Add to the acceptance test: GET `/` and `/manage` page titles show
  "Rental Manager" with "Sch. E" subtext; grep confirms SETUP.md updated.

### 1. Data store: `management.json` in the property folder
One JSON file next to the tracker workbook (same per-property pattern as
`reconciliation.json`). Schema:
- `issues[]`: id, title, status (`open`/`scheduled`/`resolved`), reported (date),
  tenant {name, email, phone}, vendor {name, phone, email}, notes[] (dated),
  linked_emails[] (subject, date, folder), expense_link (optional, e.g. "L14").
- `documents[]`: title, type (`lease`/`renewal`/`renters-insurance`/`other`),
  date, expires (optional date), source (email subject/date or file path).
Seed the SAMPLE fixture's `management.json` with realistic fake data modeled on the
real case: one open issue ("AC outdoor unit dead", tenant Sam Tenant, vendor
"Sample HVAC Co", reported 2026-07-18, 3 linked emails) and two documents (a signed
lease renewal; a renters policy with `expires` ~1 week out). Do NOT put real names,
emails, or phone numbers in the fixture — sample data only.

### 2. Generator: `engine/management_page.py`
Reads `management.json`, writes `SchE_Management.html` in the same folder. Match the
existing dashboard's visual style (same palette/fonts/card layout as
`write_dashboard` output). Sections:
1. **Issues board** — open issues first: title, status chip, reported date, tenant,
   vendor (with phone), dated notes, linked-email list. Resolved collapse below.
2. **Documents** — table with type, date, and `expires`; any document expiring
   within 30 days gets a highlighted "Upcoming" badge (e.g. the sample renters
   policy renewal).
Static generation only — page rendering makes NO network or mailbox calls. Email
linking is done upstream (Claude proposes entries into `management.json`); the page
just renders the store.

### 3. Serving
`dashboard_server.py`: add route `/manage` that serves the property folder's
`SchE_Management.html` (honoring `--tracker` the same way `/` does). Add a small
"Management" link in the dashboard header and a "Dashboard" link back from the
management page.

### 4. Acceptance test (put results in REPORT.md)
1. `python fixtures/make_fixture.py` then `python engine/reconcile.py fixtures/sample-property`
   (must be unaffected — byte-identical reconciliation outputs).
2. `python engine/management_page.py fixtures/sample-property` produces
   `SchE_Management.html` with the seeded issue and documents; renters-policy row
   shows the "Upcoming" badge.
3. `python engine/dashboard_server.py --tracker fixtures/sample-property/sample-tracker.xlsx --port 8745`:
   GET `/` still serves the dashboard; GET `/manage` serves the management page;
   header links work both ways.
4. Confirm no real personal data anywhere in committed files (grep for
   "Shin", "Wise Owl", "southcountyair", "scottshin" — all must be absent).

## Out of scope
- Automatic email fetching/linking (Claude-side via MCP, not this repo).
- Editing issues from the page (read-only render this packet; write-backs later).
- The client organizer pages (packets A & B, still queued).
- Any change to reconcile arithmetic or the Resolve flow; new dependencies; this file.
