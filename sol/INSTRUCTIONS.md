# SOL work packet — active

**Packet:** tracker-#5 · issued 2026-07-18 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`; report in the required REPORT.md format.

**Packet tracker-#4 (packaging): ACCEPTED** — v0.1.0 released. This packet fixes a
limitation found while demoing: the dashboard server cannot run against the sample
fixture, so the Resolve write-back cannot be demonstrated without real books.

## Packet tracker-#5 scope

### 1. Make `engine/dashboard_server.py` honor `--tracker` fully
Today `--tracker` overrides the workbook path for writes, but:
- `rerun_reconcile()` always reconciles the repo root (`RECONCILE ROOT`), ignoring
  the tracker override, and
- `DASHBOARD` is hard-coded to `ROOT/SchE_Dashboard.html`.

Fix: when `--tracker` is given, derive the property folder from the tracker's
directory — reconcile THAT folder and serve THAT folder's `SchE_Dashboard.html`.
Behavior with no `--tracker` stays byte-for-byte what it is now (the real Sch. E
layout must be unaffected).

### 2. Acceptance test (put results in REPORT.md)
1. `python fixtures/make_fixture.py` (fresh fixture)
2. `python engine/reconcile.py fixtures/sample-property`
3. `python engine/dashboard_server.py --tracker fixtures/sample-property/sample-tracker.xlsx --port 8745`
4. GET http://127.0.0.1:8745/ serves the SAMPLE dashboard (title "12 Sample
   Street").
5. Click/POST a Resolve on one open Review row: Review!E<row> updates in
   `sample-tracker.xlsx`, a pre-write backup appears next to it, reconcile re-runs,
   and the dashboard refresh shows the item resolved.
6. Confirm the guardrails held: only column E of an open Review row changed —
   nothing else in the workbook.

### 3. Docs touch-up
Add a short "Try the live dashboard (optional)" section to `docs/SETUP.md` after
the smoke test, using the exact command from step 3 above. Keep the same
non-technical tone as the rest of the guide.

## Out of scope
- The Client Organizer page and typed-entry form (specced separately; future
  packets).
- Any change to reconcile arithmetic, intake, or the matcher.
- New dependencies; this file.
