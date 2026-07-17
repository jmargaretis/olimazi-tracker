# SOL completion report

## Files changed

- `VERSION` — release version `0.1.0`.
- `tools/make_release.py` — Python 3 stdlib-only release builder with an explicit
  allowlist and the required `olimazi-tracker/` archive prefix.
- `.gitignore` — ignores generated `dist/` release artifacts.
- `docs/SETUP.md` — explains the extracted folder name for both a versioned release
  ZIP and GitHub's Code → Download ZIP.
- `sol/REPORT.md` — this packet completion report.

The generated `dist/olimazi-tracker-v0.1.0.zip` was used for verification and is not
committed.

## Release build

```text
> python tools/make_release.py
Created dist/olimazi-tracker-v0.1.0.zip
Files: 16

Top-level prefix valid: True
Required files present: True
Excluded entries found: 0
```

## ZIP contents

```text
olimazi-tracker/DISCLAIMER.md
olimazi-tracker/LICENSE
olimazi-tracker/README.md
olimazi-tracker/VERSION
olimazi-tracker/docs/LAYOUT-SPEC.md
olimazi-tracker/docs/SETUP.md
olimazi-tracker/engine/dashboard_server.py
olimazi-tracker/engine/intake_scan.py
olimazi-tracker/engine/match_receipts.py
olimazi-tracker/engine/new_area_setup.py
olimazi-tracker/engine/reconcile.py
olimazi-tracker/fixtures/check_fixture.py
olimazi-tracker/fixtures/make_fixture.py
olimazi-tracker/skill/olimazi-setup/SKILL.md
olimazi-tracker/skill/olimazi-setup/agents/openai.yaml
olimazi-tracker/skill/olimazi-setup/references/setup.md
```

The archive contains no `sol/`, `.git*`, `dist/`, `tools/`,
`fixtures/sample-property/`, `__pycache__/`, or `AGENTS.md` entries.

## Fresh extraction smoke test

The exact built ZIP was extracted to a new temporary directory. Paths below are
sanitized as `<fresh-temp>` so no machine-specific user path is committed.

```text
> py fixtures\make_fixture.py
Created fake sample fixture: <fresh-temp>\olimazi-tracker\fixtures\sample-property\sample-tracker.xlsx
generate exit: 0

> py engine\reconcile.py "fixtures\sample-property"
RECONCILIATION  2026-07-17
  Net income as booked : $3,295.00
  Net income corrected : $3,295.00
  Checks: 8  FAIL=1  WARN=1
  [ok] Income: YTD (Jan-Apr) == sum of 'Actual' months
  [ok] Expenses: category lines sum to Paid-YTD total
  [ok] Excel SUMIF strings match canonical labels (em-dash exact)
  [FAIL] File references resolve to real files on disk
  [ok] Insurance reimbursement is booked
  [ok] No unexplained open balances on Expenses
  [ok] No unallocated/TBD expense rows
  [warn] Accountant-review queue is clear
  Report: <fresh-temp>\olimazi-tracker\fixtures\sample-property\SchE_Reconciliation.md
reconcile exit: 1
reconciliation fails: 1
intended gardener break found: True
dashboard exists: True
```

## Additional verification

- `python -m py_compile tools/make_release.py` passed.
- The archive was inspected with Python's `zipfile` module: all 16 entries share the
  required top-level folder, all required files are present, and no excluded entry
  was found.
- No engine or skill behavior was changed.
- No new dependency was added.
- No real personal or financial data was introduced; the smoke test used only the
  fake `12 Sample Street` fixture.

## Skipped

- Publishing the GitHub Release and attaching the ZIP are reserved for planning-side
  review.
- Site changes, engine/skill behavior changes, and new dependencies were out of scope.

## Proposals

- During release review, publish `dist/olimazi-tracker-v0.1.0.zip` as the `v0.1.0`
  GitHub Release asset.
- A future packet could run the same extracted-archive smoke test in CI before a
  release is published.
