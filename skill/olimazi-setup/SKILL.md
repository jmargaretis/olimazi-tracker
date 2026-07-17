---
name: olimazi-setup
description: Set up or resume a local Olimazi finance tracker through a conversational interview and deterministic dry run. Use for requests such as "set up my tracker," "add a property," "start tracking my rental," or "start tracking my business."
---

# Olimazi Setup

Turn confirmed setup answers into a local tracker folder, `profile.json`, empty workbook,
and working dashboard. Never place a user's real profile or financial records in this
repository.

## Locate the project

Resolve the repository root two levels above this file. Run repository scripts from that
root with Python 3 and `openpyxl`; add no dependencies.

## Resume an existing tracker

If the selected tracker folder contains `profile.json`:

1. Read and summarize its name, type, applicable lines, mortgage selection, document
   folders, and recorded-only email address.
2. Do not repeat the interview.
3. Offer to run `python engine/reconcile.py "<tracker-folder>"`.
4. If accepted, report the exit status and show or open
   `<tracker-folder>/SchE_Dashboard.html`.

Do not edit the workbook during reconciliation.

## Set up a new tracker

1. Read `references/setup.md` completely.
2. Discover safe local facts where tools allow, such as whether proposed folders exist.
   Ask the user to confirm discovered values; do not make them retype known information.
3. Gather and confirm the tracker type, display name, applicable schedule lines, mortgage
   choice, document folders, and optional email address.
4. For a business, state before scaffolding that Schedule C reconciliation is still a
   setup preview and its line support is being adapted.
5. Choose a tracker folder outside the source repository. Default to
   `~/Olimazi Trackers/<safe-name>` when the user has no preference.
6. Run `engine/new_area_setup.py` with the confirmed values. Use one
   `--document-folder` argument per folder and pass the applicable lines as a
   comma-separated list. The command refuses to overwrite an existing folder.
7. Read the generated `profile.json` and confirm it matches the interview.

Example with fake data:

```powershell
python engine/new_area_setup.py --type rental --name "12 Sample Street" `
  --output "<chosen-folder>" --applicable-lines "3,9,10,14,16" `
  --mortgage no --document-folder "<confirmed-drop-folder>"
```

Email intake is future work. Record the address through `--email`; never connect, scan,
or send email during setup.

## Finish with the dry run

End every new setup by running:

```powershell
python engine/reconcile.py "<tracker-folder>"
```

Require exit `0` for an empty rental tracker. For the Schedule C setup preview, explain
that the current deterministic check is structural rather than a completed Schedule C
tax-line reconciliation. Show the user the generated empty dashboard at
`<tracker-folder>/SchE_Dashboard.html` and state that source data was not modified.
