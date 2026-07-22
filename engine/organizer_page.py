#!/usr/bin/env python3
"""Generate a static, read-only Schedule E client organizer."""

import argparse
import datetime
import json
import re
import sys
import zipfile
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

EXPENSE_LINES = {5: "Advertising", 6: "Auto and travel", 7: "Cleaning and maintenance", 8: "Commissions", 9: "Insurance", 10: "Legal and professional fees", 11: "Management fees", 12: "Mortgage interest paid to banks", 13: "Other interest", 14: "Repairs", 15: "Supplies", 16: "Taxes", 17: "Utilities", 18: "Depreciation expense or depletion", 19: "Other"}


def money(value):
    return f"${value:,.2f}"


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def tracker_path(folder):
    trackers = [p for p in folder.glob("*.xlsx") if "backup" not in p.name.lower()]
    preferred = [p for p in trackers if "tracker" in p.name.lower()]
    return (preferred or trackers)[0]


def workbook_values(folder):
    """Read workbook facts through reconcile helpers, with a stdlib XLSX fallback."""
    tracker = tracker_path(folder)
    try:
        import reconcile
        reconcile.configure(folder)
        wb = reconcile.load()
        rents = reconcile.read_income(wb["Income"])[0]
        totals = {line: 0.0 for line in EXPENSE_LINES}
        for row in reconcile.read_expenses(wb["Expenses"]):
            if row["line"] in totals:
                totals[row["line"]] += row["paid"]
        assets = [tuple(row) for row in wb["Assets"].iter_rows(values_only=True)] if "Assets" in wb.sheetnames else []
        return tracker.name, rents, totals, assets
    except (ImportError, AttributeError):
        return xlsx_fallback(tracker)


def xlsx_fallback(tracker):
    """Minimal read-only XLSX reader for installations where openpyxl is unavailable."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    with zipfile.ZipFile(tracker) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.itertext()) for node in root.findall("m:si", ns)]
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {item.attrib["Id"]: item.attrib["Target"] for item in rels}
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = {sheet.attrib["name"]: targets[sheet.attrib["{" + ns["r"] + "}id"]] for sheet in book.find("m:sheets", ns)}

        def cells(name):
            target = sheets[name].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            root = ET.fromstring(archive.read(target))
            result = {}
            for cell in root.findall(".//m:c", ns):
                value = cell.find("m:v", ns)
                if value is not None:
                    raw = value.text or ""
                    result[cell.attrib["r"]] = shared[int(raw)] if cell.attrib.get("t") == "s" else raw
            return result

        income, expenses = cells("Income"), cells("Expenses")
        rents = sum(float(income.get(f"B{row}", 0) or 0) - float(income.get(f"C{row}", 0) or 0) for row in range(6, 10))
        totals = {line: 0.0 for line in EXPENSE_LINES}
        for row in range(5, 500):
            match = re.search(r"L\s*(\d+)", str(expenses.get(f"D{row}", "")))
            if match and int(match.group(1)) in totals:
                totals[int(match.group(1))] += float(expenses.get(f"F{row}", 0) or 0)
        return tracker.name, rents, totals, []


def intake_summary(folder):
    path = folder / "_Inbox" / "_manifest.md"
    if not path.exists():
        return 0, 0.0
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\*\*(\d+) item\(s\) awaiting review", text)
    amounts = [float(value.replace(",", "")) for value in re.findall(r"\$([\d,]+(?:\.\d{2})?)", text)]
    return (int(match.group(1)) if match else 0), sum(amounts)


def chip(confirmed, path):
    date = confirmed.get(path)
    return f'<span class=confirmed>confirmed {escape(str(date))}</span>' if date else '<span class=unconfirmed>unconfirmed</span>'


def display(value):
    return "Yes" if value is True else "No" if value is False else "Not answered" if value is None else str(value)


def render(folder: Path) -> Path:
    profile = load_json(folder / "profile.json", {})
    reconciliation = load_json(folder / "reconciliation.json", {})
    management = load_json(folder / "management.json", {})
    confirmed, filing = profile.get("confirmed", {}), profile.get("filing", {})
    tracker, rents, expense_totals, assets = workbook_values(folder)
    intake_count, intake_total = intake_summary(folder)
    open_items = [item for item in reconciliation.get("open_items", []) if not item.get("resolved")]
    alerts = sum(check.get("status") == "FAIL" for check in reconciliation.get("checks", []))
    filing_labels = [("tax_year", "Tax year"), ("on_extension", "On extension?"), ("extension_by_default", "Extension by default?"), ("estimated_payments_made", "Estimated payments made?"), ("books_closed_through", "Books closed through"), ("fair_rental_days", "Fair rental days"), ("personal_use_days", "Personal-use days"), ("depreciation_booked", "Depreciation booked?"), ("made_1099_payments", "Made payments requiring Form 1099?"), ("will_file_1099s", "Will required Forms 1099 be filed?")]
    flags = "".join(f'<div class=flag><span class=box>{"☑" if filing.get(key) is True else "☐"}</span><div><b>{label}</b><br>{escape(display(filing.get(key)))}</div>{chip(confirmed, "filing." + key)}</div>' for key, label in filing_labels)
    if filing.get("extension_by_default"):
        nudge = '<aside class="nudge habit"><b>Your default: file an extension every year ✓</b></aside>'
    elif not filing.get("on_extension") or "filing.on_extension" not in confirmed:
        nudge = '<aside class=nudge><b>Many self-managing landlords file an extension every year by default — it turns the April rush into an October review and costs nothing to file.</b><p>An extension extends your time to <strong>FILE</strong>, not your time to <strong>PAY</strong> — settle expected tax by the April deadline.</p><p>Confirm what\'s right for your situation with your preparer.</p></aside>'
    else:
        nudge = ""
    owner, preparer = profile.get("owner", {}), profile.get("preparer") or {}
    emails = owner.get("emails", [])
    emails = [emails] if isinstance(emails, str) else emails
    preparer_html = (f'<div class=person><h3>Preparer</h3><b>{escape(preparer.get("name", ""))}</b><br>{escape(preparer.get("firm", ""))}<br>{escape(preparer.get("email", ""))}<br>{escape(preparer.get("phone", ""))}</div>' if preparer else '<div class="person empty"><h3>Preparer</h3><b>Add your preparer</b><p>Add your preparer so this organizer is ready for a clean handoff.</p></div>')
    properties = profile.get("properties", [])
    property_html = "".join(f'<details class=property open><summary>{escape(p.get("address", "Unnamed property"))}</summary><div class=propertygrid><span>Type: <b>{escape(p.get("type", ""))}</b> {chip(confirmed, f"properties.{i}.type")}</span><span>Ownership: <b>{escape(display(p.get("ownership_pct")))}%</b> {chip(confirmed, f"properties.{i}.ownership_pct")}</span><span>In service: <b>{escape(p.get("in_service_date", ""))}</b> {chip(confirmed, f"properties.{i}.in_service_date")}</span><span>Rental / personal days: <b>{escape(display(filing.get("fair_rental_days")))} / {escape(display(filing.get("personal_use_days")))}</b></span></div></details>' for i, p in enumerate(properties))
    connections = [("Owner", owner.get("name", ""), ", ".join(emails), "Profile: owner"), ("Preparer", preparer.get("name", ""), " · ".join(filter(None, [preparer.get("firm"), preparer.get("email"), preparer.get("phone")])), "Profile: preparer")]
    for issue in management.get("issues", []):
        for role in ("tenant", "vendor"):
            person = issue.get(role) or {}
            if person.get("name"):
                connections.append((role.title(), person["name"], " · ".join(filter(None, [person.get("email"), person.get("phone")])), f'Issue: {issue.get("title", "Untitled issue")}'))
    connection_html = "".join(f'<div class=connection><b>{escape(role)} · {escape(str(name))}</b><span>{escape(str(contact))}</span><small>Appears in: {escape(str(appears))}</small></div>' for role, name, contact, appears in connections if name)
    expense_rows = "".join(f'<tr><td>Line {line}</td><td>{escape(label)}</td><td class=num>{money(expense_totals[line])}</td></tr>' for line, label in EXPENSE_LINES.items())
    asset_html = "<p>None recorded.</p>" if not assets else "".join(f"<p>{escape(' · '.join(str(v) for v in row if v is not None))}</p>" for row in assets[1:])
    claim_html = "".join(f'<div class=claim><b>Insurance claim {escape(str(claim.get("claim_ref", "")))}</b><p>{escape(str(claim.get("activity", "")))}</p><strong>Alert total: {money(float(claim.get("alert_total", 0) or 0))}</strong></div>' for claim in management.get("insurance_claims", []))
    first_address = properties[0].get("address", "") if properties else ""
    html = f'''<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Rental Organizer — Sch. E — {escape(first_address)}</title>
<style>:root{{--cream:#F4EDDD;--card:#FBF8EF;--crimson:#9B1C2E;--olive:#566123;--sand:#D2C8B0;--ink:#2B2A26;--muted:#7D7666;font-family:'Inter','Segoe UI',sans-serif}}*{{box-sizing:border-box}}body{{margin:0 auto;background:var(--cream);color:var(--ink);padding:26px 20px;max-width:1040px}}nav,.card{{background:var(--card);border:1px solid var(--sand);border-radius:14px;box-shadow:0 1px 2px #0000000f}}nav{{display:flex;align-items:center;justify-content:space-between;padding:13px 18px}}.brand{{font-size:21px;font-weight:800}}.brand span{{color:var(--muted);font-weight:500}}.links{{display:flex;gap:14px}}a{{color:var(--olive);font-size:13px;font-weight:700;text-decoration:none}}.hero{{padding:28px 6px 8px}}h1{{font-size:34px;margin:0}}.hero p,.muted,small{{color:var(--muted)}}.card{{padding:18px;margin-top:18px;break-inside:avoid}}h2{{font-size:12px;margin:0 0 13px;text-transform:uppercase;letter-spacing:.08em;color:var(--olive)}}h3{{margin:0 0 8px}}.flags,.identity,.propertygrid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}.flag,.person,.connection,.claim{{background:white;border:1px solid var(--sand);border-radius:11px;padding:12px}}.flag{{display:flex;align-items:center;gap:9px}}.box{{font-size:21px;color:var(--olive)}}.confirmed,.unconfirmed{{margin-left:auto;border-radius:999px;padding:2px 7px;font-size:10px;font-weight:700}}.confirmed{{background:#e7ecd6;color:#404a18}}.unconfirmed{{background:#eee7da;color:var(--muted)}}.nudge{{margin-top:13px;border-left:5px solid #9c6f19;background:#f3e6c7;padding:13px;border-radius:8px}}.nudge p{{margin:7px 0 0}}.habit{{border-color:var(--olive);background:#e7ecd6}}.identity{{grid-template-columns:1fr 1fr}}.empty{{border-style:dashed}}details{{margin-top:10px}}summary{{cursor:pointer;font-weight:700;color:var(--olive)}}.propertygrid{{padding:12px 0}}.propertygrid span{{padding:8px;background:white;border-radius:8px}}.connection{{display:grid;grid-template-columns:1fr 1fr;margin-top:8px}}.connection small{{grid-column:1/-1;margin-top:5px}}table{{width:100%;border-collapse:collapse;font-size:14px}}td{{padding:8px 4px;border-bottom:1px solid var(--sand)}}.num{{text-align:right;font-variant-numeric:tabular-nums}}.metrics{{display:flex;gap:20px;flex-wrap:wrap}}.metric b{{display:block;font-size:25px}}footer{{color:var(--muted);font-size:12px;text-align:center;margin:24px 0}}@media(max-width:700px){{.flags,.identity,.propertygrid{{grid-template-columns:1fr}}}}@media print{{body{{background:#fff;padding:0;max-width:none}}nav{{box-shadow:none}}.card{{box-shadow:none;break-inside:avoid}}details{{break-inside:avoid}}details>summary{{list-style:none}}details>*{{display:block!important}}.links{{display:none}}}}</style></head><body>
<nav><div class=brand>olimazi<span>.online</span></div><div class=links><a href="/">Dashboard</a><a href="/manage">Management</a><a href="/organizer">Organizer</a></div></nav>
<div class=hero><h1>Rental Organizer</h1><p>{escape(first_address)} · {len(properties)} property · Tax year {escape(display(filing.get("tax_year")))}</p></div>
<section class=card><h2>Filing flags</h2><div class=flags>{flags}</div>{nudge}</section>
<section class=card><h2>Identity · {len(properties)} property</h2><div class=identity><div class=person><h3>Owner</h3><b>{escape(owner.get("name", ""))}</b> {chip(confirmed, "owner.name")}<br>{escape(", ".join(emails))} {chip(confirmed, "owner.emails")}</div>{preparer_html}</div>{property_html}</section>
<details class=card><summary>Connections ({len([item for item in connections if item[1]])})</summary><p class=muted>Read-only roster aggregated from profile and management records.</p>{connection_html}</details>
<section class=card><h2>Income</h2><div class=metrics><div class=metric><b>{money(rents)}</b>Rents received · booked</div><div class=metric><b>{intake_count}</b>Intake items awaiting review · {money(intake_total)}</div></div></section>
<section class=card><h2>Schedule E expenses · lines 5–19</h2><table>{expense_rows}</table></section>
<section class=card><h2>Assets / depreciation</h2>{asset_html}</section>
<section class=card><h2>Attention</h2><div class=metrics><div class=metric><b>{intake_count}</b>Intake pending</div><div class=metric><b>{len(open_items)}</b>Open review items</div><div class=metric><b>{alerts}</b>Alert total SUM</div></div>{claim_html}</section>
<footer>Generated {datetime.date.today().isoformat()} · Source workbook: {escape(tracker)} · This is a practical organizer, not tax advice. Confirm filing positions and deadlines with your preparer.</footer></body></html>'''
    output = folder / "SchE_Organizer.html"
    output.write_text(html, encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description="Generate a read-only client organizer.")
    parser.add_argument("property_folder", type=Path)
    args = parser.parse_args()
    print(f"Created organizer: {render(args.property_folder.resolve())}")


if __name__ == "__main__":
    main()
