# SOL work packet — active

**Packet:** tracker-#8 · issued 2026-07-20 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`; report in the required REPORT.md format.

**Packet tracker-#7 (Management page + Rental Manager rename): ACCEPTED** — live in fixture.

## Packet tracker-#8 scope — Client Organizer page (organizer packet A)

Page 4: `SchE_Organizer.html` — a generated client organizer in the spirit of a
CPA organizer. Its core purpose is a **trust layer**: show what the workbook and
stores currently BELIEVE (addresses, contacts, filing status, booked totals) so
the owner — or an accountant on handoff — can verify the system sees their
situation correctly. Read-only render this packet; confirm/correct write-backs
and typed entry are packet B.

### 1. Data store: `profile.json` in the property folder
Same per-property pattern as `reconciliation.json` / `management.json`. Schema:
- `owner`: name, email(s)
- `preparer`: name, firm, email, phone (all optional — organizer renders an
  "add your preparer" empty-state prompt when absent)
- `filing`: tax_year, on_extension (bool), estimated_payments_made (bool),
  books_closed_through (month), fair_rental_days, personal_use_days,
  depreciation_booked (bool), made_1099_payments (bool|null), will_file_1099s (bool|null)
- `properties[]`: address, type, ownership_pct, in_service_date
- `confirmed`: map of field-path → ISO date of last human confirmation (empty ok)
Seed the SAMPLE fixture with fake data consistent with existing fixtures
("12 Sample Street", owner "Sam Owner" sam@example.com, preparer "Pat Preparer"
of "Sample Tax Co", pat@example.com, 555-0177). No real names/emails/
addresses anywhere in committed files.

### 2. Generator: `engine/organizer_page.py`
Reads `profile.json`, the workbook (via existing reconcile helpers),
`reconciliation.json`, `management.json`, and `_Inbox/_manifest.md` if present.
Writes `SchE_Organizer.html` in the property folder. Match the dashboard's
visual style. Sections, in order:
1. **Header / filing flags** — tax year + checkbox-style rendering of every
   `filing` field (on extension? · estimated payments? · books closed through ·
   fair rental / personal-use days · depreciation booked? · the two Schedule E
   1099 questions). Unconfirmed values (no `confirmed` entry) get a muted
   "unconfirmed" chip — the visual heart of the trust layer.
   **Extension nudge (John's feature, 2026-07-20):** when `on_extension` is
   false or unconfirmed, render a friendly callout beside the flag recommending
   the extension-by-default habit. Required wording elements (exact copy may be
   polished but must contain all three): (a) the nudge — "Many self-managing
   landlords file an extension every year by default — it turns the April rush
   into an October review and costs nothing to file." (b) the caveat, visually
   inseparable from the nudge — "An extension extends your time to FILE, not
   your time to PAY — settle expected tax by the April deadline." (c) the
   product's standard preparer language — "Confirm what's right for your
   situation with your preparer." Also add `filing.extension_by_default` (bool)
   to profile.json: when true, the callout renders as the user's own confirmed
   habit ("Your default: file an extension every year ✓") instead of a
   suggestion. Suppressing/toggling from the page itself is packet B write-path
   work; this packet renders state only.
2. **Identity block** — owner name/email(s) and **preparer card** (name, firm,
   email, phone — or the "add your preparer" empty state); per property (header
   shows property COUNT, each expands): address, type, ownership %, in-service
   date, fair rental/personal-use days. Same confirmed/unconfirmed chips.
2b. **Connections** (expandable, collapsed by default) — one roster of every
   person/entity the system knows, aggregated across stores: owner and preparer
   (profile.json), tenants and vendors (management.json issues), each with
   contact info and a "appears in" line (e.g. "Issue: AC outdoor unit dead").
   Read-only aggregation — no new data entry this packet.
3. **Income** — rents received (booked, from workbook) + count/total of intake
   items awaiting review.
4. **Expense skeleton** — EVERY Schedule E line 5–19 listed even at $0
   (advertising · auto/travel · cleaning & maintenance · commissions · insurance ·
   legal & professional · management fees · mortgage interest · other interest ·
   repairs · supplies · taxes · utilities · depreciation · other), booked amount
   per line.
5. **Assets / depreciation** — assets placed in service this year, or "none recorded."
6. **Attention** — intake items awaiting review (count) · open review items ·
   **alert total SUM** · insurance-claim block if management.json carries one
   (claim ref, activity, its alert total).
7. **Footer** — generated date · source workbook filename · the existing
   "practical organizer, not tax advice" disclaimer language.
Print-friendly: sensible `@media print` (no dark background, cards flow).
Static generation only — no network or mailbox calls at render time.

### 3. Serving
`dashboard_server.py`: add route `/organizer` (honoring `--tracker` like `/` and
`/manage`). Add "Organizer" to the cross-page header links on all three pages.

### 4. Acceptance test (results in REPORT.md)
1. `python engine/reconcile.py fixtures/sample-property` unaffected —
   byte-identical reconciliation outputs.
2. `python engine/organizer_page.py fixtures/sample-property` produces
   `SchE_Organizer.html`: all 15 expense lines present (including $0 lines),
   filing flags render with unconfirmed chips, property count = 1, alert SUM
   matches the dashboard's alert total; preparer card renders from the seeded
   fixture preparer ("Sample Tax Co", "Pat Preparer", pat@example.com); the
   Connections section lists owner + preparer + the sample issue's tenant and
   vendor, each with an "appears in" line. Also verify the empty state: remove
   preparer from a copy of profile.json, regenerate, confirm the "add your
   preparer" prompt renders. Extension nudge: with fixture `on_extension: false`,
   confirm the callout renders with all three required elements (nudge, FILE-vs-
   PAY caveat, preparer line); flip `extension_by_default: true` in a copy,
   regenerate, confirm it renders as the confirmed-habit variant instead.
3. Server: GET `/`, `/manage`, `/organizer` all serve; header links between all
   three pages work.
4. Print preview sanity: page renders legibly with print styles (screenshot).
5. Grep committed files for real personal data ("Shin", "Wise Owl",
   "southcountyair", "scottshin", "Margaretis", "Via Madera", "jmargaretis") —
   all must be absent.

## Out of scope
- Confirm/correct WRITE-BACKS and the typed-entry expense form (packet B —
  propose-only, same review queue; do not build any write path this packet).
- Automatic population of profile.json from setup (future; hand-seeded now).
- Any change to reconcile arithmetic; new dependencies; this file.
