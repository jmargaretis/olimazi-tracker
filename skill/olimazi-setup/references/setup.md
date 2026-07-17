# Olimazi setup interview

Use this interview to confirm only what cannot be discovered safely. Olimazi is a
record-keeping organizer, not tax, legal, or accounting advice. Do not decide a user's
tax treatment; mark uncertain line choices for confirmation with their preparer.

## What are we tracking?

Confirm:

- **Rental property (Schedule E)** or **small business (Schedule C)**.
- The display name or address the user wants shown in their private local tracker.
- The destination tracker folder. Keep real profile data outside the source repository.

For a small business, say plainly that Schedule C engine support is still being adapted.
The generated dashboard is an empty structural preview, not a completed Schedule C
filing workflow.

## Which schedule lines apply?

Walk only the common lines relevant to the selected tracker. Record line numbers in
`profile.json`; the workbook and dashboard visually mute lines not selected.

Common Schedule E prompts:

- Line 3 — rents received
- Line 5 — advertising
- Line 6 — auto and travel
- Line 7 — cleaning and maintenance
- Line 8 — commissions
- Line 9 — insurance
- Line 10 — legal and professional fees
- Line 11 — management fees
- Line 12 — mortgage interest
- Line 13 — other interest
- Line 14 — repairs
- Line 15 — supplies
- Line 16 — taxes
- Line 17 — utilities
- Line 18 — depreciation
- Line 19 — other

Ask whether a rental is owned outright or has a mortgage. If owned outright, record
`mortgage: false` and omit Line 12 unless the user identifies another applicable reason.
If the answer is uncertain, record the user's current selection and recommend preparer
confirmation instead of resolving it yourself.

For Schedule C, record the lines the user or their preparer already expects. Do not
translate Schedule E line meanings into Schedule C categories.

## Where do documents arrive?

Discover and confirm each local drop folder. Record absolute folder paths, but do not
move, delete, or scan their contents during setup. The generated intake scanner remains
copy-only and can later be run with `--dry-run`.

Ask whether documents also arrive by email. If so, record the email address with status
`recorded_only`. Email intake is a future packet: do not connect a mailbox or create
email rules.

## Scaffold

Run `engine/new_area_setup.py` with the confirmed answers. It creates:

- `profile.json`
- `tracker.xlsx` using the four-tab fixture layout with empty data rows
- `_System/intake_scan.py`
- `_Inbox`, `_Archive`, `_OutOfScope`, `Reference`, and `Reports` folders

The generator must leave `fixtures/make_fixture.py` demo behavior unchanged and refuse
to overwrite an existing tracker folder.

## Confirm with the dry run

Run `engine/reconcile.py` against the new tracker folder. Confirm that it writes:

- `SchE_Reconciliation.md`
- `reconciliation.json`
- `SchE_Dashboard.html`

For an empty rental tracker, require zero failures and show the empty dashboard. Summarize
what was created, where it lives, which lines are active, and what remains only recorded
for later.
