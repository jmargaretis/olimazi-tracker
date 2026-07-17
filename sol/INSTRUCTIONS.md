# SOL work packet — active

**Packet:** tracker-#2 · issued 2026-07-17 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`. Direct-change authority within scope only.

**Packet tracker-#1: ACCEPTED.** Review notes: fixture + engine run reproduced exactly
on the planning side; SETUP.md cold-tested — the python.org link was wrong
(downloads/windows has no big button; fixed to /downloads), the `py` launcher and
PowerShell address-bar steps verified on a real Windows machine, all `[VERIFY]` tags
now cleared. Your "John's" wording catch was correct and has been fixed. Your fixture
regression-check proposal is folded into this packet (item 3).

## Packet tracker-#2 scope — the intake skill

Build `skill/olimazi-setup/` — the conversational first-run setup that turns this repo
from a demo into someone's own tracker. Model it on the interview→config pattern:
discover with tools where possible, ask the user only to confirm, write everything to
a config that later runs read.

### 1. `skill/olimazi-setup/SKILL.md`
Frontmatter (name, description with trigger phrases like "set up my tracker",
"add a property", "start tracking my rental/business") + the run procedure:
- If `profile.json` exists in the property folder → summarize it and offer to
  reconcile instead of re-interviewing.
- Otherwise read `references/setup.md` and run the interview.
- End every setup with the read-only dry run: generate the property folder, run
  `engine/reconcile.py` on it, show the user their empty-but-working dashboard.

### 2. `skill/olimazi-setup/references/setup.md`
The interview. Sections:
- **What are we tracking?** Rental property (Schedule E) or a small business
  (Schedule C — note the engine's Sch C support is still being adapted; set
  expectations honestly). Name/address of the property or business.
- **Which schedule lines apply?** Walk the common lines (insurance, repairs,
  professional fees, taxes, etc.); record which apply so the dashboard can
  grey out the rest. Owned outright vs mortgage (Line 12 n/a pattern).
- **Where do documents arrive?** Drop folder location(s); email note for later
  (email intake is a future packet — record the address, don't wire it).
- **Scaffold** via `engine/new_area_setup.py` + a fresh workbook from the fixture
  generator's layout (reuse `fixtures/make_fixture.py` structure with the user's real
  property name and EMPTY data rows — factor a shared helper if that avoids
  duplicating layout code, but keep make_fixture.py's demo behavior unchanged).
- **Write `profile.json`** (property name, type, applicable lines, folders,
  anticipated-items placeholders) and confirm with the dry run.

### 3. Fixture regression check (your proposal, accepted)
`fixtures/check_fixture.py`: regenerates the workbook, runs the reconciler,
asserts exit 1 / exactly one failure / the missing locksmith reference. Plain
Python, no new dependencies. Add one line to README pointing at it.

### 4. Report
Overwrite `sol/REPORT.md`: files, how you tested the interview flow end-to-end
(walk a fake user through it in your report), regression-check output, proposals.

## Out of scope
- Email intake wiring, scheduled tasks, packaging/releases
- Engine guardrail changes; real data; dependencies beyond Python 3 + openpyxl
- This file
