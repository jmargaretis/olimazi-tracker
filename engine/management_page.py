#!/usr/bin/env python3
"""Render a property's management.json as a static, read-only HTML page."""

import argparse
import datetime
import json
from html import escape
from pathlib import Path


def source_text(source):
    if isinstance(source, str):
        return source
    if isinstance(source, dict):
        return " · ".join(str(source.get(key, "")) for key in ("subject", "date") if source.get(key))
    return ""


def render(property_folder: Path) -> Path:
    data = json.loads((property_folder / "management.json").read_text(encoding="utf-8"))
    today = datetime.date.today()

    def issue_card(issue):
        tenant, vendor = issue.get("tenant", {}), issue.get("vendor", {})
        notes = "".join(f"<li><time>{escape(n.get('date', ''))}</time> {escape(n.get('text', ''))}</li>" for n in issue.get("notes", [])) or "<li>None</li>"
        emails = "".join(f"<li>{escape(e.get('subject', ''))} <span>· {escape(e.get('date', ''))} · {escape(e.get('folder', ''))}</span></li>" for e in issue.get("linked_emails", [])) or "<li>None</li>"
        expense = f"<span class=expense>{escape(issue['expense_link'])}</span>" if issue.get("expense_link") else ""
        status = escape(issue.get("status", "open"))
        return f"""<article class=issue><div class=issuehead><h3>{escape(issue.get('title', 'Untitled issue'))}</h3><span class="status {status}">{status.title()}</span>{expense}</div>
<p class=reported>Reported {escape(issue.get('reported', ''))}</p><div class=people><div><b>Tenant</b><br>{escape(tenant.get('name', ''))}</div><div><b>Vendor</b><br>{escape(vendor.get('name', ''))}<br>{escape(vendor.get('phone', ''))}</div></div>
<h4>Notes</h4><ul>{notes}</ul><h4>Linked emails</h4><ul>{emails}</ul></article>"""

    issues = sorted(data.get("issues", []), key=lambda i: (i.get("status") == "resolved", i.get("reported", "")))
    active = "".join(issue_card(i) for i in issues if i.get("status") != "resolved") or "<p class=muted>No open issues.</p>"
    resolved = "".join(issue_card(i) for i in issues if i.get("status") == "resolved")
    resolved_html = f"<details><summary>Resolved issues</summary>{resolved}</details>" if resolved else ""
    rows = []
    for document in data.get("documents", []):
        expires, upcoming = document.get("expires", ""), ""
        if expires:
            try:
                if 0 <= (datetime.date.fromisoformat(expires) - today).days <= 30:
                    upcoming = " <span class=upcoming>Upcoming</span>"
            except ValueError:
                pass
        rows.append(f"<tr><td>{escape(document.get('title', ''))}</td><td>{escape(document.get('type', ''))}</td><td>{escape(document.get('date', ''))}</td><td>{escape(expires)}{upcoming}</td><td>{escape(source_text(document.get('source', '')))}</td></tr>")

    html = f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Rental Manager — Sch. E — Management</title>
<style>:root{{--cream:#F4EDDD;--card:#FBF8EF;--crimson:#9B1C2E;--olive:#566123;--sand:#D2C8B0;--ink:#2B2A26;--muted:#7D7666;font-family:'Inter','Segoe UI',-apple-system,Roboto,Helvetica,Arial,sans-serif}}*{{box-sizing:border-box}}body{{margin:0 auto;background:var(--cream);color:var(--ink);padding:26px 20px;max-width:1040px}}nav,.card{{background:var(--card);border:1px solid var(--sand);border-radius:14px;box-shadow:0 1px 2px rgba(43,42,38,.06)}}nav{{display:flex;align-items:center;justify-content:space-between;padding:13px 18px}}.brand{{font-size:21px;font-weight:800}}.brand span{{color:var(--muted);font-weight:500}}nav a{{color:var(--olive);font-size:13px;font-weight:700;text-decoration:none}}.hero{{padding:28px 6px 10px}}h1{{font-size:34px;margin:0;letter-spacing:-.02em}}h1 small{{font-size:15px;color:var(--muted);font-weight:600;letter-spacing:0;margin-left:8px}}.hero p,.muted,.reported,li span{{color:var(--muted)}}.card{{padding:18px;margin-top:18px}}.card>h2{{font-size:12px;margin:0 0 12px;text-transform:uppercase;letter-spacing:.08em;color:var(--olive)}}.issue{{background:#fff;border:1px solid var(--sand);border-radius:12px;padding:14px;margin-bottom:12px}}.issuehead{{display:flex;align-items:center;gap:8px}}h3{{margin:0;font-size:18px}}h4{{margin:14px 0 5px;font-size:12px;text-transform:uppercase;color:var(--olive)}}.status,.expense,.upcoming{{border-radius:999px;padding:2px 8px;font-size:11px;font-weight:700}}.status.open{{background:#f6e0dd;color:var(--crimson)}}.status.scheduled{{background:#f3e6c7;color:#8a5a12}}.status.resolved{{background:#e7ecd6;color:#404a18}}.expense{{background:#efe7d6;color:var(--muted)}}.people{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}ul{{margin:4px 0;padding-left:20px;font-size:13px}}li{{margin:4px 0}}details{{margin-top:14px}}summary{{cursor:pointer;font-weight:700;color:var(--olive)}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{text-align:left;padding:9px 6px;border-bottom:1px solid var(--sand);vertical-align:top}}th{{color:var(--muted)}}.upcoming{{background:#f3e6c7;color:#8a5a12;white-space:nowrap}}@media(max-width:700px){{.people{{grid-template-columns:1fr}}table{{display:block;overflow-x:auto}}h1{{font-size:28px}}}}</style></head>
<body><nav><div class=brand>olimazi<span>.online</span></div><a href="/">Dashboard</a></nav><div class=hero><h1>Rental Manager<small>Sch. E</small></h1><p>Property management · static local view</p></div><section class=card><h2>Issues board</h2>{active}{resolved_html}</section><section class=card><h2>Documents</h2><table><thead><tr><th>Title</th><th>Type</th><th>Date</th><th>Expires</th><th>Source</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section></body></html>"""
    output = property_folder / "SchE_Management.html"
    output.write_text(html, encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description="Generate a static property management page.")
    parser.add_argument("property_folder", type=Path)
    args = parser.parse_args()
    print(f"Created management page: {render(args.property_folder.resolve())}")


if __name__ == "__main__":
    main()
