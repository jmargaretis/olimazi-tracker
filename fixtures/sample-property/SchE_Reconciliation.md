# Rental Manager — Sch. E
## Reconciliation Report
**Tracker:** 12 Sample Street · **Generated:** 2026-07-21 · _Deterministic check — recomputed from raw rows, no model judgment._

## Verdict: **1 ALERT(S) FOUND**  (1 warning(s))

## Bottom line
| Line | Amount |
|---|---|
| 3 — Rents received (YTD) | $7,150 |
| 9 — Insurance | $1,200 |
| 10 — Professional fees | $350 |
| 14 — Repairs | $955 |
| 20 — Total expenses | $3,855 |
| **21 — Net income (as booked)** | **$3,295** |
| **Grand total (L3 − L20)** | **$3,295** |

## Checks
- ✅ **Income: YTD (Jan-Apr) == sum of 'Actual' months** — YTD net $7,150 vs Actual-flagged months $7,150. Summary Line 3 links to Income!D19 (Jan-Apr).
- ✅ **Expenses: category lines sum to Paid-YTD total** — Sum of L-line categories $3,855 vs sum of all Paid-YTD $3,855.
- ✅ **Excel SUMIF strings match canonical labels (em-dash exact)** — All expense labels match the exact SUMIF text.
- ❌ **File references resolve to real files on disk** — Dangling File References (the document isn't where the tracker says): row 12 (Sample Gardener): source-docs/missing-gardener-invoice.pdf
- ✅ **Insurance reimbursement is booked** — No outstanding received-but-unbooked reimbursement detected.
- ✅ **No unexplained open balances on Expenses** — All contracted amounts fully paid (Balance = 0).
- ✅ **No unallocated/TBD expense rows** — No TBD expense rows.
- ⚠️ **Accountant-review queue is clear** — 1 item(s) flagged for a preparer to confirm: Sample Mutual — $-300

## Flagged for accountant review
- **Sample Mutual — $-300** (Expenses row 11) — Confirm the negative repair contra treatment with the preparer.

_Re-run any time with `python _System/reconcile.py`. Exit code = number of alerts._