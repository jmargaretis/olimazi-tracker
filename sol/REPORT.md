# SOL completion report

## Files added

- `.gitattributes` — preserves generated PDF and XLSX files as binary in Git.
- `.gitignore` — excludes local Python bytecode caches.
- `fixtures/make_fixture.py` — deterministic Python 3 + `openpyxl` fixture generator.
- `fixtures/sample-property/sample-tracker.xlsx` — fake 12 Sample Street tracker with
  Income, Expenses, Sch. E Summary, and Review tabs.
- `fixtures/sample-property/source-docs/` — sanitized placeholder policy, receipt,
  invoice, assessment, consultation, and reimbursement records.
- `fixtures/sample-property/SchE_Dashboard.html` — generated dashboard.
- `fixtures/sample-property/SchE_Reconciliation.md` — generated readable reconciliation.
- `fixtures/sample-property/reconciliation.json` — generated machine-readable results.
- `docs/SETUP.md` — nontechnical Windows setup and five-minute smoke test.

The fixture deliberately does not include
`source-docs/missing-locksmith-receipt.pdf`; that is the packet's one intended
dangling reference.

## Reconciler output

```text
RECONCILIATION  2026-07-17
  Net income as booked : $3,620.00
  Net income corrected : $3,620.00
  Checks: 8  FAIL=1  WARN=1
  [ok] Income: YTD (Jan-Apr) == sum of 'Actual' months
  [ok] Expenses: category lines sum to Paid-YTD total
  [ok] Excel SUMIF strings match canonical labels (em-dash exact)
  [FAIL] File references resolve to real files on disk
  [ok] Insurance reimbursement is booked
  [ok] No unexplained open balances on Expenses
  [ok] No unallocated/TBD expense rows
  [warn] Accountant-review queue is clear
  Report: fixtures\sample-property\SchE_Reconciliation.md
```

The command exits `1`, as required. The only failure is Expenses row 12,
`source-docs/missing-locksmith-receipt.pdf`. The warning is the intended
accountant-review flag for the negative insurance reimbursement contra entry.

## Engine patches

None. The fixture reached the target using the existing reconciler.

## `[VERIFY]` list from the setup guide

- Confirm the current python.org Windows page still presents the main
  **Download Python 3** button.
- Confirm the current Python installer still offers an **Add python.exe to PATH**
  checkbox at the bottom of its first window.
- Confirm typing `powershell` in File Explorer's address bar still opens
  PowerShell in that folder on supported Windows versions.
- If `py` is not recognized, confirm rerunning the installer with the PATH option
  is still the correct first remedy.

## Proposals

- Add a small automated fixture regression check in a future packet that regenerates
  the workbook and asserts exit `1`, exactly one failure, and the expected missing
  locksmith reference.
- Replace the pre-existing phrase “John's explicit confirmation” in
  `engine/dashboard_server.py` with role-based wording such as “the owner's explicit
  confirmation.” It looks personal, so it is flagged here as required; changing the
  engine was outside this packet.
