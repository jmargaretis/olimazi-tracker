# Workbook layout spec (what the engine expects)

**Source of truth is the code** — `engine/reconcile.py` (`read_income`, `read_expenses`,
`read_review_open`) and `engine/dashboard_server.py` (`resolve_row`). This file is the
human-readable map; if it ever disagrees with the code, the code wins and this file
should be fixed.

The tracker is one `.xlsx` ("`*tracker*.xlsx`" in the property folder or its parent —
filenames containing "backup" or "test" are ignored by the picker) with four tabs:

## 1. Income
- Monthly rows with a Status column marking months as **Actual** vs projected.
- `D19` = YTD net income cell the Summary links to (Line 3).

## 2. Expenses
- Header block ends at row 4; data rows follow.
- Column C: description · Column D: **schedule line label** · Column F: amount paid ·
  Column I: file reference (path relative to the property folder, `/` separators) ·
  Column J: notes.
- Line labels use an **em dash** and must match the Summary SUMIF strings exactly,
  e.g. `L9 — Insurance`, `L14 — Repairs`. A plain hyphen silently drops the row —
  the reconciler checks for this.
- Reimbursements (e.g. insurance proceeds) are booked as a **negative contra row**
  against the related expense line, with a note containing `ACCOUNTANT REVIEW:` —
  the reconciler surfaces those notes into a standing queue.

## 3. Sch. E Summary
- `B5`: Fair Rental Days.
- Line rows: label in column B, `SUMIF(Expenses!D:D, "<exact label>", Expenses!F:F)`
  in column C, notes in column D. Line 3 links to `Income!D19`. Line 20 sums the
  category lines; Line 21 = Line 3 + Line 4 − Line 20.
- The workbook stores **formulas only, no cached values** — tools must never trust a
  cell's stored result; the reconciler recomputes everything from raw rows.

## 4. Review
- Headers on row 4: `Type | Item | Issue | Action Needed | Status` (columns A–E).
- Data from row 5. An item is **open** unless its Status starts with `Resolved`.
- The dashboard server's only write is Status (column E) of an open row.
