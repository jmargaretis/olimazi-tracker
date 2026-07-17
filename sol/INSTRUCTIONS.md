# SOL work packet — active

**Packet:** tracker-#3 · issued 2026-07-17 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`. Direct-change authority within scope only.

**Packet tracker-#2: ACCEPTED.** Independent verification on the planning side: regression
check PASS; scaffold → empty tracker reconciled 8/8 at $0.00; overwrite refusal works;
profile-driven dashboard renders the property name and greys non-selected lines; skill
validated. The profile.json read-only design in reconcile.py is exactly right. Your two
proposals are acknowledged: native Schedule C support is queued as its own future packet;
the legacy-branch cleanup will ride along in a later hygiene packet.

## Packet tracker-#3 scope — the receipt↔row matcher

Build `engine/match_receipts.py`: for tracker rows that have no File Reference, find the
likely source document — and **propose, never book**. This is the engine's strictest
guardrail surface; the design rules below are requirements, not suggestions.

### 1. Matching logic
For each Expenses row with an empty File Reference cell:
- Candidate pool: files in the property folder tree plus any `document_folders` from
  `profile.json` (skip generated outputs: dashboards, reports, reconciliation.json).
- Score on three signals: filename/date within ±5 days of the row date (many filenames
  carry ISO dates — parse them; fall back to file modified time), amount appearing in
  the filename (exact or with .00 stripped), and vendor tokens from the row description.
- **Two-plausible-candidates rule:** if more than one candidate scores as a match,
  propose NEITHER — list both under "ambiguous" instead. A wrong link is worse than
  no link.

### 2. Propose-only output (hard rule)
- The matcher NEVER writes to the tracker workbook, never moves/renames/deletes files.
- Output: `MatchProposals.md` (human-readable: row, vendor, amount, proposed file,
  the evidence for the match) + `match_state.json` (machine state) in the property
  folder.
- Miss tracking lives in `match_state.json` (not the tracker): rows searched and not
  found accumulate a miss count across runs; at 2+ misses a row moves to a
  **"Need from you"** section at the top of MatchProposals.md (vendor, date, amount).
- Accepting a proposal is a human/assistant action outside this tool — the .md should
  say exactly what to paste into the File Reference cell for each proposal.

### 3. Prove it on the fixture
Extend the fixture story: add to `fixtures/make_fixture.py` a second intentional
scenario — one expense row with NO file reference whose true receipt DOES exist in
`source-docs/` (matchable by date+amount+vendor), plus keep the missing-locksmith row
(which the matcher should report as a miss, since its file genuinely doesn't exist).
Then extend `fixtures/check_fixture.py` to also run the matcher and assert: exactly one
proposal (the right file), the locksmith row in misses, zero writes to the workbook
(compare file hash before/after the matcher runs).

### 4. Report
Overwrite `sol/REPORT.md`: files, matcher output pasted from the fixture run, the
hash-unchanged proof, edge cases you considered, proposals.

## Out of scope
- Writing anything into any .xlsx; email search (folders only for now); packaging
- Engine guardrail changes; new dependencies beyond Python 3 + openpyxl
- This file
