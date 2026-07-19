# Olimazi Tracker

A finance tracker you own. Local files, deterministic math, zero running cost — for
rental (Schedule E) and small-business (Schedule C) bookkeeping, with an AI assistant
handling the judgment calls and a Python engine keeping the numbers honest.

User-facing rental pages are titled **Rental Manager** with **Sch. E** subtext. The
future Schedule C counterpart will be titled **Business Manager** with **Sch. C**
subtext.

**Status: working prototype, being packaged.** Follow along at [olimazi.online](https://olimazi.online).

## The idea in one line

Capture documents broadly **for free**, review them **periodically with judgment**
(that's the AI's job), and keep the numbers honest with a **deterministic reconciler** —
so the spreadsheet, the dashboard, and the source documents can never quietly disagree.

## Three layers

| Layer | What runs | Cost | Job |
|---|---|---|---|
| **Capture** | `engine/intake_scan.py` | $0, no AI | Copies finance-looking files from drop folders into a review queue. Never deletes originals; dedupes by hash. |
| **Review** | your AI assistant (scheduled or on demand) | plan usage | Reads the queue, proposes ledger rows. Proposes — never books. |
| **Reconcile** | `engine/reconcile.py` | $0, no AI | Recomputes every tax-schedule line from raw rows, checks file references / labels / balances, and generates the dashboard FROM the spreadsheet so they can't drift. Exit code = number of breaks. |

Plus `engine/dashboard_server.py`: a localhost server that adds one-click "Resolve"
buttons to the dashboard — the only thing it can write is the Status column of an open
Review item, and it re-reconciles after every write.

## What this is not

- **Not tax advice.** It's an organizer. Confirm figures with your tax preparer (see DISCLAIMER.md).
- **Not a bank feed.** It works from the documents and statements you already have.
- **Not a subscription.** Your records are `.xlsx` and PDFs in folders you own.

## Layout

- `engine/` — the four Python scripts (Python 3 + openpyxl; nothing else).
- `fixtures/` — sample property with fake data for testing and demos (in progress).
- `docs/` — workbook layout spec and (coming) the plain-English setup guide.
- `sol/` — work-packet protocol for the build agents (see AGENTS.md).

Run `python fixtures/check_fixture.py` to regenerate the fake fixture in isolation
and confirm its one intentional missing-reference failure.
