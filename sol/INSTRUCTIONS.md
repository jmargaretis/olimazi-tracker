# SOL work packet — active

**Packet:** tracker-#6 · issued 2026-07-19 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`; report in the required REPORT.md format.

**Packet tracker-#5 (fixture dashboard): ACCEPTED** — commit 7cb284a. Live demo
passed: sample dashboard served, Resolve write-back verified with guardrails held.

## Packet tracker-#6 scope

### 1. Whole-dollar display
`money()` in `engine/reconcile.py` (line ~129) renders cents (`${x:,.2f}`).
Change DISPLAY ONLY to whole dollars (`${x:,.0f}`, standard rounding) everywhere
amounts render — reconciliation report, dashboard, verdict lines. All arithmetic,
comparisons, and the `CENTS` tolerance stay at full precision; only formatting
changes. Stored numeric values (e.g. `total_expenses` in JSON output) keep cents.

### 2. Grand total line
Add a **Grand total** line at the bottom of the line-item table in BOTH the
generated `SchE_Reconciliation.md` and the dashboard: net result = Line 3 rents
received minus Line 20 total expenses, bolded, whole-dollar display per §1.
Label it exactly `Grand total (L3 − L20)`.

### 3. BREAK → ALERTS rename
Rename the verdict terminology everywhere a human sees it:
- `engine/reconcile.py` lines ~529 and ~726: `N BREAK(S)` → `N ALERT(S)`,
  `N BREAK(S) FOUND` → `N ALERT(S) FOUND`.
- Any dashboard badge text/CSS class or title derived from it.
- `docs/SETUP.md` line ~77 promises testers "The red **1 BREAK(S)** badge" —
  update to ALERT(S) in the SAME packet so docs never drift from the product.
Internal variable names (`fails` etc.) may stay; this is user-facing wording.

### 4. Regenerate the sample fixture
After §1–§3, regenerate so committed sample outputs match the code:
1. `python fixtures/make_fixture.py`
2. `python engine/reconcile.py fixtures/sample-property`
Commit the regenerated outputs. Do NOT commit `engine/intake_state.json` or any
`*.pre-resolve-backup.xlsx` (now gitignored — machine-specific/personal data).

### 5. Acceptance test (put results in REPORT.md)
1. Fresh fixture + reconcile per §4.
2. Confirm `SchE_Reconciliation.md` shows whole-dollar amounts, the
   `Grand total (L3 − L20)` line, and `ALERT(S)` verdict wording.
3. `python engine/dashboard_server.py --tracker fixtures/sample-property/sample-tracker.xlsx --port 8745`
   → dashboard shows whole dollars, grand total line, red ALERT(S) badge.
4. `grep -ri "BREAK" engine/ docs/ fixtures/sample-property/` returns nothing
   user-facing (generated outputs and docs are clean).
5. Confirm reconcile arithmetic unchanged: same pass/fail results as before the
   packet on the sample fixture (only wording/formatting moved).

## Out of scope
- Client Organizer page and typed-entry form (future packets A & B).
- Any change to reconcile arithmetic, intake, matcher, or tolerances.
- New dependencies; this file.
