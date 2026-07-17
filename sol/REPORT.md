# SOL completion report

## Files changed

- `skill/olimazi-setup/SKILL.md` — first-run and resume procedure, including the
  mandatory read-only reconciliation dry run.
- `skill/olimazi-setup/references/setup.md` — confirmation-first interview for tracker
  type, schedule lines, mortgage status, document folders, and recorded-only email.
- `skill/olimazi-setup/agents/openai.yaml` — generated skill-list metadata.
- `engine/new_area_setup.py` — self-contained rental/business scaffold that refuses
  overwrite, creates an empty workbook, preserves the copy-only intake scanner, and
  writes `profile.json`.
- `fixtures/make_fixture.py` — reusable `build_empty_workbook()` path; the existing
  `build_workbook()` demonstration behavior is unchanged.
- `engine/reconcile.py` — read-only `profile.json` support for tracker name/type and
  applicable-line display. Arithmetic and source-data guardrails are unchanged.
- `fixtures/check_fixture.py` — isolated fixture regression check.
- `fixtures/sample-property/` generated workbook, JSON, report, and dashboard —
  regenerated from fake data to match the current generator and reconciler.
- `README.md` — one-line regression-check command.

## Fake interview walkthrough

I walked a fake user through a rental setup using only `12 Sample Street`:

1. Tracking type: rental / Schedule E.
2. Display name: `12 Sample Street`.
3. Applicable lines: 3, 9, 10, 14, and 16.
4. Mortgage: no; Line 12 remained unselected.
5. Document arrival: a temporary fake local folder.
6. Email: `records@example.invalid`, recorded with status `recorded_only`; no mailbox
   was connected.
7. Scaffold command exited `0` and created `profile.json`, `tracker.xlsx`, the
   copy-only intake scanner, and the standard folders outside the repository.
8. `engine/reconcile.py` exited `0`: 8 checks, 0 failures, 0 warnings, $0.00 net
   income, and an empty working dashboard.
9. A second invocation against the same destination exited `1` and refused to
   overwrite it.
10. The generated intake scanner compiled and its `--dry-run` exited `0` without
    capturing or modifying any source files.

I also ran a fake business setup. It exited `0`, recorded
`schedule_c_setup_preview`, displayed the Schedule C preview warning, and produced the
structural empty dashboard without claiming completed Schedule C line support.

## Workbook and skill verification

- Skill validator: `Skill is valid!`
- Python compile check: passed for the scaffolder, reconciler, generator, and fixture
  regression script.
- Workbook inspection: four expected tabs; formulas only on `Sch. E Summary`; no
  formula-error strings found.
- Visual render: all four tabs inspected; empty entry rows, headers, validations, and
  muted non-applicable lines were legible.
- Dashboard applicability check: an omitted Line 10 rendered with the `not selected`
  label and inactive styling.
- Data-hygiene scan: no new personal or financial data; all committed examples remain
  fake `12 Sample Street` data.

## Fixture regression output

```text
Fixture regression: PASS
  reconcile exit: 1
  failures: 1
  intended missing reference: missing-locksmith-receipt.pdf
```

The regression runs in a temporary isolated tree, so it does not dirty the committed
sample workbook.

## Skipped

- Email intake wiring, scheduled tasks, packaging, and releases were out of scope.
- No live user data was used and no tracker generated during the walkthrough is being
  committed.

## Proposals

- Complete a native Schedule C workbook/line map and use Schedule C-specific output
  filenames in a future packet. The current business path is intentionally labeled as
  a setup preview.
- In a future cleanup packet, remove the now-unused legacy external-project scaffold
  branch from `engine/new_area_setup.py` after confirming no older installation still
  invokes it.
