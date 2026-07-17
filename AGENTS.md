# SOL operating contract

Same protocol as `olimazi-online`:

When the owner says "check GitHub for instructions" (for the tracker), read the active
packet in `sol/INSTRUCTIONS.md`. Execute only that packet's stated scope, commit to
`main`, then overwrite `sol/REPORT.md` with the completion report (files changed, how
it was verified, anything skipped, out-of-scope proposals).

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
