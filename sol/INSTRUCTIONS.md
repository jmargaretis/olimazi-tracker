# SOL work packet — active

**Packet:** tracker-#1 · issued 2026-07-17 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md` (same contract as olimazi-online). Direct-change authority within scope only.

## Context

This repo holds the sanitized public engine of the Olimazi finance tracker. The four
scripts in `engine/` were lifted from a working private system and scrubbed of personal
data; they run but have never been exercised against fixture data in this repo. Your
job is to make the repo self-demonstrating.

## Packet tracker-#1 scope

### 1. Build the fixture generator
Create `fixtures/make_fixture.py` (Python 3 + openpyxl only): generates
`fixtures/sample-property/sample-tracker.xlsx` — the fake "12 Sample Street" rental —
conforming to `docs/LAYOUT-SPEC.md` (the spec defers to `engine/reconcile.py`; read the
code, the code wins). Include: 4 months of actual rent + projections, 6–10 expense rows
across at least L9/L10/L14/L16 with exact em-dash labels, one negative reimbursement
contra row with an `ACCOUNTANT REVIEW:` note, a few file references pointing at small
placeholder PDFs/text files you also generate, at least one intentionally-dangling file
reference, and a Review tab with 3 open + 2 resolved items. Formulas only in the
Summary tab — no cached values.

### 2. Prove the engine runs on it
Run `python engine/reconcile.py "fixtures/sample-property"` . Target state: all checks
executed, with exactly the breaks the fixture intends (the dangling reference) — i.e.
exit code 1, and the generated `SchE_Dashboard.html` + reconciliation report land in
the fixture folder. Commit the generated dashboard/report as demo artifacts. If the
engine crashes on the fixture, fix the FIXTURE first; only patch `engine/` if the code
itself is broken in a way the private system can't be (note any engine patch
prominently in REPORT.md — the planning side must mirror it to the private system).

### 3. Draft the setup guide
Write `docs/SETUP.md` for a **non-technical reader** (think: someone who has never
opened a terminal). Plain English, zero jargon, numbered steps, one install path
(Windows first), a "what this is NOT" box (mirroring DISCLAIMER.md), and a 5-minute
smoke test that ends with the reader seeing the sample dashboard in their browser.
Where a step can't be verified from this repo alone (e.g. exact Python installer
screens), write it best-effort and mark it `[VERIFY]` — the planning side will test
the guide cold on a real Windows machine.

### 4. Report
Overwrite `sol/REPORT.md`: files added, engine-run output (paste the check summary),
any engine patches, `[VERIFY]` list from the guide, proposals.

## Out of scope
- Changing engine guardrails or the deterministic design (see AGENTS.md)
- Real data of any kind; new dependencies beyond Python 3 + openpyxl
- Packaging/releases, licensing changes, this file
