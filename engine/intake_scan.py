#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Schedule E intake scanner — the free, local CAPTURE layer.

Scans capture sources (the Google Drive drop folder + the Downloads folder),
COPIES anything that looks like a property document/receipt/photo into one
review staging folder (_Inbox/), and logs it in a manifest for review. It never
deletes or moves the original, never books anything, and uses ZERO model tokens.

The model-driven READING of these files (extracting amounts from a photographed
receipt, proposing tracker rows) happens later in the cloud review step — this
script only gathers and stages.

Usage:
    python _System/intake_scan.py            # capture + write manifest
    python _System/intake_scan.py --dry-run  # show what it would capture, copy nothing

Design notes:
- Drop folder = explicit human intent -> capture ALL supported file types.
- Downloads = mixed bag -> capture supported types only when the name matches a
  property keyword, so it doesn't hoover up installers, resumes, recipes, etc.
- Dedupe by SHA1 across runs (intake_state.json) so re-running never re-copies.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROP = os.path.join(os.path.dirname(ROOT), "Sch E Inbox")  # phone / anyone drops here (vault, OneDrive-synced)
DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
INBOX = os.path.join(ROOT, "_Inbox")               # review staging
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intake_state.json")
MANIFEST = os.path.join(INBOX, "_manifest.md")

SUPPORTED = {".pdf", ".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif",
             ".tif", ".tiff", ".docx", ".eml", ".msg"}
SKIP = {".exe", ".msi", ".zip", ".msix", ".dmg", ".iso", ".py", ".md", ".json",
        ".js", ".ts", ".ini", ".gdoc", ".gsheet", ".lnk", ".tmp", ".crdownload"}

# Downloads is incidental and full of unrelated files, so it requires a STRICT
# match to 12 Sample Street or a known the sample property vendor — generic words like "rent",
# "lease", "invoice", "hoa", "policy" pulled in other properties (45 Example Ave),
# the personal home (the owner's home), and unrelated HOAs. The Drive drop folder stays
# capture-all because dropping a file there is explicit intent.
STRICT_SAMPLE = [
    "12 sample", "12 sample", "12 sample", "sample-plumber", "sample-contractor", "sample-contractor",
    "sample-vendor", "sample-vendor", "sample-carrier", "SAMPLE-001", "REF-0000",
    "sample-insurer", "sample-insurer.example", "POLICY-0000", "sample-insurer", "sp1", "Sample HOA",
    "anytown landscape", "sample-tenant", "sample-tenant",
]
# Broader set for scanning MIXED local folders (salvage / prior years) where both
# properties and tax/insurance docs live — catches 45 Example Ave + historical files
# the strict the sample property list would miss, while still skipping random personal photos.
RENTAL_KEYWORDS = sorted(set(STRICT_SAMPLE + [
    "45 Example Ave", "sample-tenant", "sample-tenant", "samplestreet", "rental", "lease", "tenant",
    "landlord", "insurance", "policy", "renters", "expenses", "receipt", "invoice",
    "tax", "1098", "mortgage", "hoa", "depreciation", "schedule e", "sch e",
    "sch. e", "escrow", "property", "deposit",
]))
PROPERTY_KEYWORDS = STRICT_SAMPLE  # category-guess context
KEYWORDS = {"property": STRICT_SAMPLE, "rental": RENTAL_KEYWORDS}

CATEGORY_RULES = [
    (("sample-insurer", "sample-insurer.example", "sample-insurer", "policy", "dwelling", "renters", "insurance"), "Insurance (L9)"),
    (("sample-plumber", "plumb", "sample-contractor", "sample-contractor", "coastal", "restoration", "water", "drywall", "hvac", "repair"), "Repairs (L14)"),
    (("sp1", "mold", "inspection", "attorney", "legal", "professional"), "Professional fees (L10)"),
    (("hoa", "Sample HOA", "management"), "Management fees (L11)"),
    (("sample-carrier", "SAMPLE-001", "REF-0000", "claim"), "Insurance claim SAMPLE-001 (review)"),
    (("rent", "tenant", "lease", "sample-tenant"), "Income / lease doc"),
    (("property tax", "1098", "mortgage", "escrow"), "Taxes / mortgage"),
    (("invoice", "receipt"), "Expense — needs categorization"),
]


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def guess_category(name):
    low = name.lower()
    for keys, cat in CATEGORY_RULES:
        if any(k in low for k in keys):
            return cat
    return "Unsorted — needs review"


def name_matches(name, keywords):
    low = name.lower()
    return any(k in low for k in keywords)


def _iter_files(base, recursive):
    if recursive:
        for dp, _, fns in os.walk(base):
            for n in fns:
                yield os.path.join(dp, n)
    else:
        for n in os.listdir(base):
            p = os.path.join(base, n)
            if os.path.isfile(p):
                yield p


def candidates(extra_sources):
    """Yield (path, source_label, mode) for each existing source.

    Standing sources: the Drive drop folder (mode 'all') and Downloads (mode
    'property' = strict the sample property). Ad-hoc sources come from `--scan <folder>` and are
    walked recursively; default mode 'rental' (broad property/tax match). mode 'all'
    captures every supported type; otherwise the filename must match the mode's
    keyword set. Capturing is always a copy — originals are never touched.
    """
    srcs = []
    if os.path.isdir(DROP):
        srcs.append((DROP, "drop", "all", False))
    if os.path.isdir(DOWNLOADS):
        srcs.append((DOWNLOADS, "downloads", "property", False))
    for path, mode in extra_sources:
        if os.path.isdir(path):
            lbl = "".join(c for c in os.path.basename(os.path.normpath(path)) if c.isalnum())[:12].upper() or "SCAN"
            srcs.append((path, lbl, mode, True))
        else:
            print(f"  (skipped — not a folder): {path}")
    for base, label, mode, recursive in srcs:
        for p in _iter_files(base, recursive):
            yield p, label, mode


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    extra, mode = [], None
    i = 0
    while i < len(args):
        if args[i] == "--scan" and i + 1 < len(args):
            extra.append(args[i + 1]); i += 2; continue
        if args[i] == "--mode" and i + 1 < len(args):
            mode = args[i + 1]; i += 2; continue
        i += 1
    extra_sources = [(p, mode or "rental") for p in extra]

    os.makedirs(INBOX, exist_ok=True)
    state = {"captured": {}}
    if os.path.exists(STATE):
        try:
            state = json.load(open(STATE, encoding="utf-8"))
        except Exception:
            pass
    seen = set(state.get("captured", {}).keys())

    captured, skipped = [], []
    for path, source, src_mode in candidates(extra_sources):
        ext = os.path.splitext(path)[1].lower()
        name = os.path.basename(path)
        if ext in SKIP or ext not in SUPPORTED:
            continue
        if src_mode != "all" and not name_matches(name, KEYWORDS.get(src_mode, RENTAL_KEYWORDS)):
            continue
        try:
            digest = sha1(path)
        except Exception:
            continue
        if digest in seen:
            continue  # already captured in a prior run
        cat = guess_category(name)
        dest_name = f"{source.upper()}__{name}"
        dest = os.path.join(INBOX, dest_name)
        rec = {"name": name, "source": source, "category": cat,
               "size": os.path.getsize(path), "src_path": path,
               "captured_at": datetime.now().isoformat(timespec="seconds"),
               "sha1": digest, "staged_as": dest_name}
        if dry:
            skipped.append(rec)
            continue
        # collision-safe copy; never touch the original
        i = 1
        while os.path.exists(dest):
            dest = os.path.join(INBOX, f"{source.upper()}_{i}__{name}")
            i += 1
        shutil.copy2(path, dest)
        rec["staged_as"] = os.path.basename(dest)
        state.setdefault("captured", {})[digest] = rec
        seen.add(digest)
        captured.append(rec)

    if not dry:
        state["last_run"] = datetime.now().isoformat(timespec="seconds")
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        write_manifest(state)

    label = "WOULD CAPTURE" if dry else "CAPTURED"
    items = skipped if dry else captured
    scanned = "drop + Downloads"
    if extra_sources:
        scanned += " + " + ", ".join(os.path.basename(os.path.normpath(p)) for p, _ in extra_sources)
    print(f"Intake scan {date.today()} — sources: {scanned}")
    print(f"  {label}: {len(items)} new file(s); _Inbox now tracks {len(state.get('captured', {}))} item(s).")
    for r in items:
        print(f"   [{r['source']}] {r['name']}  -> {r['category']}")
    if not items:
        print("  Nothing new to capture.")
    print(f"  Manifest: {MANIFEST}")
    return 0


def write_manifest(state):
    allrows = sorted(state.get("captured", {}).values(),
                     key=lambda r: r["captured_at"], reverse=True)
    awaiting = [r for r in allrows if r.get("disposition", "awaiting") == "awaiting"]
    done = [r for r in allrows if r.get("disposition", "awaiting") != "awaiting"]
    L = ["# Sch. E Intake — Review Queue",
         f"_Updated {datetime.now():%Y-%m-%d %H:%M}. Files captured from the Drive drop "
         "folder and Downloads, staged for review. Originals were left in place; nothing "
         "is booked. The weekly cloud review reads these and proposes tracker rows._\n",
         f"**{len(awaiting)} item(s) awaiting review in `_Inbox/`** "
         f"({len(done)} already filed/dismissed).\n",
         "| Captured | Source | File (staged name) | Guessed category | Size |",
         "|---|---|---|---|---|"]
    for r in awaiting:
        L.append(f"| {r['captured_at'][:10]} | {r['source']} | `{r['staged_as']}` | "
                 f"{r['category']} | {r['size']/1024:.0f} KB |")
    if not awaiting:
        L.append("| — | — | _queue empty_ | — | — |")
    if done:
        L.append("\n## Filed / dismissed (kept in the log so they won't be re-captured)")
        L.append("| File | Disposition |")
        L.append("|---|---|")
        for r in done:
            L.append(f"| {r['name']} | {r['disposition']} |")
    L.append("\n_After a row is booked into the tracker, set its disposition (or just delete "
             "its file from `_Inbox/`). The hash stays logged so it won't be re-captured._")
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
