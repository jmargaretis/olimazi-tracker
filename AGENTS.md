# SOL operating contract

Same protocol as `olimazi-online`:

When the owner says "check GitHub for instructions" (for the tracker), read the active
packet in `sol/INSTRUCTIONS.md`. Execute only that packet's stated scope, commit to
`main`, then overwrite `sol/REPORT.md` with the completion report in the required
format below.

Direct changes are authorized only within the packet. Put any out-of-scope idea in
`sol/REPORT.md` as a proposal instead of implementing it.

Repo-specific rules:
- Never introduce real personal or financial data — all examples and fixtures use the
  fake `12 Sample Street` property. If you spot anything that looks personal, flag it
  in REPORT.md immediately.
- The engine's guardrails are product requirements: the reconciler and intake never
  modify source data; the dashboard server writes only the Review Status column;
  arithmetic stays deterministic (no AI in the reconcile path). Do not weaken them.
- Owner's operating preference: momentum over polish — working and shippable beats
  perfect.

## Required REPORT.md format

Every report uses exactly these sections, in this order. Write "None" under a section rather than omitting it — the reviewer checks your claims against the diff, so a missing section reads as a hidden change.

```markdown
# SOL completion report — packet #N

## Status
COMPLETE | PARTIAL | BLOCKED — one line of summary.

## Changes
Every file touched, with one line each: what changed and why. This list must
match the diff exactly — a file in the diff but not listed here is a protocol
violation.

## Deviations
Anything done differently from the packet's stated instructions, and why.
Includes files touched that the packet didn't name.

## Skipped / unverified
Packet items not done, or done but not verified, and why.

## Blocked / questions
If any packet instruction was ambiguous or impossible: STOP on that item rather
than improvising, and put the question here. A good question beats a guessed
implementation.

## Proposals
Out-of-scope ideas for a future packet. Never implemented.
```

If Status is BLOCKED, commit whatever safe partial work exists plus the report — never leave the repo in a broken state.
