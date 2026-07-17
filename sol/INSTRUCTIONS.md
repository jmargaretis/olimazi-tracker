# SOL work packet — active

**Packet:** tracker-#4 · issued 2026-07-17 · authored by Claude (planning side)
**Protocol:** see `AGENTS.md`. Direct-change authority within scope only.

**Packet tracker-#3: ACCEPTED with one review fix.** The matcher itself verified
perfectly on the planning side (proposal, ambiguity refusal, miss escalation, hash
proof). The review fix: clearing the locksmith row's dangling reference silently
removed the fixture's break demo — the reconciler exited 0 while docs/SETUP.md still
promised users "exactly one FAIL." Restored via a new Sample Gardener row with an
intentionally dangling reference (non-empty ref, so your matcher scenarios are
untouched); check_fixture now asserts exit 1 + that specific dangling file; SETUP.md
wording updated. Lesson for future packets: when a change alters generated-output
behavior, grep docs/ for promises about that behavior.

## Packet tracker-#4 scope — packaging

Make the repo releasable as a versioned zip a non-technical user downloads and runs.

### 1. `VERSION` file
Repo root, containing `0.1.0`.

### 2. `tools/make_release.py`
Python 3 stdlib only. Builds `dist/olimazi-tracker-v<VERSION>.zip` containing:
- `engine/`, `skill/`, `docs/`, `fixtures/make_fixture.py`, `fixtures/check_fixture.py`
- `README.md`, `LICENSE`, `DISCLAIMER.md`, `VERSION`
- EXCLUDES: `sol/`, `.git*`, `dist/`, generated outputs under `fixtures/sample-property/`,
  `__pycache__`, `AGENTS.md`, `tools/`
The zip's top-level folder must be `olimazi-tracker/` (so Extract All gives a clean
folder name — SETUP.md Part 2 step 5 should be updated to match the extracted name
for the release-zip path while still working for the GitHub Code→Download ZIP path;
one short note covering both names is fine).

### 3. Prove the zip
In your report: build the zip, extract it to a fresh temp folder, and run the SETUP.md
smoke test from the extracted tree (fixture generate → reconcile exits 1 with the one
intended gardener break → dashboard file exists). Paste the transcript.

### 4. `.gitignore`
Add `dist/`.

### 5. Report
Overwrite `sol/REPORT.md`: files, zip content listing, extraction smoke-test
transcript, proposals.

## Out of scope
- Publishing the GitHub Release itself (planning side does that at review)
- Site changes (separate packet on the site repo)
- Engine/skill behavior changes; new dependencies; this file
