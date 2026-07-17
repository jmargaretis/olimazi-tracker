# SOL completion report

## Files changed

- `engine/match_receipts.py` — propose-only receipt matcher with conservative scoring,
  ambiguity refusal, persistent miss counts, and human/machine outputs.
- `fixtures/make_fixture.py` — adds one matchable unlinked Sample Electric expense and
  keeps the genuinely missing Sample Locksmith expense as an empty File Reference.
- `fixtures/check_fixture.py` — validates the proposal, miss escalation, ambiguity
  refusal, clean reconciliation, and unchanged workbook hash.
- `fixtures/sample-property/sample-tracker.xlsx` — regenerated fake workbook.
- `fixtures/sample-property/source-docs/2026-04-10_sample-electric_145.pdf` — fake
  uniquely matchable receipt.
- `fixtures/sample-property/MatchProposals.md` and `match_state.json` — generated
  matcher outputs after two fixture runs.
- `fixtures/sample-property/SchE_Dashboard.html`, `SchE_Reconciliation.md`, and
  `reconciliation.json` — regenerated deterministic outputs.

The locksmith row's previous dangling File Reference was cleared so it obeys the
packet's eligibility rule: the matcher examines rows whose File Reference cell is empty.
The reconciler therefore now exits `0`; the missing receipt is tracked in matcher state
instead of masquerading as a workbook link.

## Matcher output from the fixture

```text
Receipt matcher: 1 proposal(s), 0 ambiguous, 1 miss(es)
  Proposals: fixtures/sample-property/MatchProposals.md
```

```markdown
## Need from you

- Expenses row 12: **Sample Locksmith** · 2026-04-05 · $95.00
  (2 searches with no match)

## Proposals

### Expenses row 13 — Sample Electric — $145.00

- Proposed file: `source-docs/2026-04-10_sample-electric_145.pdf`
- Evidence: date 2026-04-10 from filename is 0 day(s) from row date;
  filename contains amount 145; filename contains row token(s): electric
- Human action: paste `source-docs/2026-04-10_sample-electric_145.pdf`
  into the File Reference cell.

## Ambiguous

_None._
```

The tool did not accept the proposal or write the path into the workbook.

## Workbook hash proof

The committed fixture was generated, reconciled, and then matched twice:

```text
workbook_sha256_before=f9d4573a57e699c1d8d27e84928bfdb3dcf97a3130976aa479345f4194991d00
workbook_sha256_after =f9d4573a57e699c1d8d27e84928bfdb3dcf97a3130976aa479345f4194991d00
workbook_hash_unchanged=True
```

The isolated regression also compares SHA-256 before and after every matcher scenario.

## Verification

`python fixtures/check_fixture.py`:

```text
Fixture regression: PASS
  reconcile exit: 0; failures: 0
  matcher: 1 proposal, 0 ambiguous, 1 miss
  proposal: source-docs/2026-04-10_sample-electric_145.pdf
  miss after two runs: Sample Locksmith (Need from you)
  ambiguity rule: 2 plausible files -> 0 proposals, 1 ambiguous
  workbook sha256 unchanged: 394c578977d080b819ce4c251d5755c357cd96659f016e81a6b94237c09369ef
```

Additional checks:

- Python compile check passed for the matcher, fixture generator, and regression test.
- Workbook inspection found both empty File Reference cells and no formula-error strings.
- The Expenses tab was visually rendered; the new rows match existing styles and remain
  legible.
- Data-hygiene scan found no new personal or financial data; all fixtures remain fake
  `12 Sample Street` data.

## Edge cases considered

- A filename date exactly five days away is allowed, but cannot create a proposal by
  itself.
- Generic tokens such as `sample`, `receipt`, and `repair` do not count as vendor
  evidence.
- Negative amounts are compared by absolute value.
- ISO dates with separators or compact `YYYYMMDD` are parsed; otherwise modified time
  is used.
- Missing or invalid `profile.json` is treated as no external document folders.
- Missing external folders are skipped; overlapping folders are deduplicated.
- Generated dashboards, reconciliation outputs, and prior matcher outputs are excluded
  from candidates.
- More than one candidate scoring at least two signals produces zero proposals and an
  `ambiguous` entry listing every plausible file.
- If a row's identifying vendor/date/amount changes, its miss count restarts instead of
  inheriting stale state from the old row.

## Skipped

- No `.xlsx` writes, proposal acceptance, file moves/renames/deletes, email search,
  packaging, or new dependencies were added.

## Proposals

- A future explicitly confirmed acceptance workflow could paste a selected proposal
  into File Reference while preserving a separate audit trail.
- A future OCR/metadata packet could add document-content signals for receipts whose
  filenames contain no useful date, amount, or vendor tokens.
