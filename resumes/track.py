#!/usr/bin/env python3
"""
CLI for the CV tracker sheet. Treat the sheet as your application DB.

Commands:
    list                                show all applications (table)
    show <company>                      show one row, all fields
    status <company> <status>           set Status
    set <company> <field> <value>       set any manual field
    note <company> <text>               append to Notes (timestamped)
    applied <company> [date]            mark Submitted + set Date Applied (today if omitted)

Examples:
    python3 resumes/track.py list
    python3 resumes/track.py status visa Interview
    python3 resumes/track.py applied bakuun
    python3 resumes/track.py set sonar Contact "Jane Doe <jane@sonar.io>"
    python3 resumes/track.py note flo_energy "Recruiter call Thu 3pm"

Manual fields: Status, Date Applied, Source, Contact, Next Action, Notes
Auto fields (managed by sync_tracker.py): Company, Role, Headline, Theme, HTML, PDF, Updated
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime

from gspread.utils import rowcol_to_a1

from sheet_common import (
    AUTO_COLS,
    HEADERS,
    MANUAL_COLS,
    REACHED_VIA_OPTIONS,
    STATUS_OPTIONS,
    get_or_create_ws,
    load_env,
    open_sheet,
)


def connect():
    env = load_env()
    sh = open_sheet(env)
    ws = get_or_create_ws(sh, env["GOOGLE_SHEET_TAB"], cols=len(HEADERS) + 2, rows=200)
    return ws


def fetch_all(ws):
    """Single read. Returns (headers, rows_with_row_numbers)."""
    values = ws.get_all_values()
    if not values:
        sys.exit("Sheet is empty. Run setup_sheet.py + sync_tracker.py first.")
    headers = values[0]
    rows = [(i + 2, row) for i, row in enumerate(values[1:]) if row and row[0]]
    return headers, rows


def find_row(rows, company: str) -> tuple[int, list[str]]:
    company_lower = company.lower()
    matches = [(rn, r) for rn, r in rows if r[0].lower() == company_lower]
    if not matches:
        partial = [(rn, r) for rn, r in rows if company_lower in r[0].lower()]
        if len(partial) == 1:
            return partial[0]
        if len(partial) > 1:
            sys.exit(f"Ambiguous: matches {[r[0] for _, r in partial]}")
        sys.exit(f"No company matching '{company}'. Use `list` to see options.")
    return matches[0]


def col_letter(name: str) -> str:
    idx = HEADERS.index(name) + 1
    return rowcol_to_a1(1, idx)[:-1]


def cmd_list(args):
    ws = connect()
    headers, rows = fetch_all(ws)
    cols = ["Company", "Role", "Status", "Date Applied", "Next Action"]
    idxs = [headers.index(c) for c in cols]
    widths = [max(len(c), *(len(r[i]) for _, r in rows)) for c, i in zip(cols, idxs)]
    widths = [min(w, 50) for w in widths]
    sep = "  "
    print(sep.join(c.ljust(w) for c, w in zip(cols, widths)))
    print(sep.join("-" * w for w in widths))
    for _, r in rows:
        cells = [(r[i][:50] if len(r[i]) > 50 else r[i]).ljust(w) for i, w in zip(idxs, widths)]
        print(sep.join(cells))


def cmd_show(args):
    ws = connect()
    headers, rows = fetch_all(ws)
    _, row = find_row(rows, args.company)
    width = max(len(h) for h in headers)
    for h, v in zip(headers, row):
        marker = "  " if h in AUTO_COLS else "* "
        print(f"{marker}{h.ljust(width)}  {v}")
    print("\n* = editable")


def update_cell(ws, row_num: int, field: str, value: str):
    if field not in MANUAL_COLS:
        sys.exit(f"'{field}' is auto-managed. Editable: {', '.join(MANUAL_COLS)}")
    col = col_letter(field)
    ws.update(range_name=f"{col}{row_num}", values=[[value]], value_input_option="USER_ENTERED")


def cmd_status(args):
    if args.status not in STATUS_OPTIONS:
        sys.exit(f"Invalid status. Choose: {', '.join(STATUS_OPTIONS)}")
    ws = connect()
    _, rows = fetch_all(ws)
    row_num, row = find_row(rows, args.company)
    update_cell(ws, row_num, "Status", args.status)
    print(f"{row[0]}: Status -> {args.status}")


def cmd_set(args):
    ws = connect()
    _, rows = fetch_all(ws)
    row_num, row = find_row(rows, args.company)
    field = next((m for m in MANUAL_COLS if m.lower() == args.field.lower()), None)
    if not field:
        sys.exit(f"Unknown field '{args.field}'. Editable: {', '.join(MANUAL_COLS)}")
    update_cell(ws, row_num, field, args.value)
    print(f"{row[0]}: {field} -> {args.value}")


def cmd_note(args):
    ws = connect()
    headers, rows = fetch_all(ws)
    row_num, row = find_row(rows, args.company)
    existing = row[headers.index("Notes")]
    stamp = date.today().strftime("%Y-%m-%d")
    line = f"[{stamp}] {args.text}"
    new = f"{existing}\n{line}" if existing else line
    update_cell(ws, row_num, "Notes", new)
    print(f"{row[0]}: note added")


def cmd_link(args):
    ws = connect()
    _, rows = fetch_all(ws)
    row_num, row = find_row(rows, args.company)
    update_cell(ws, row_num, "Link", args.url)
    print(f"{row[0]}: Link -> {args.url}")


def cmd_email(args):
    ws = connect()
    _, rows = fetch_all(ws)
    row_num, row = find_row(rows, args.company)
    update_cell(ws, row_num, "Email", args.email)
    print(f"{row[0]}: Email -> {args.email}")


def cmd_via(args):
    if args.channel not in REACHED_VIA_OPTIONS:
        sys.exit(f"Invalid channel. Choose: {', '.join(REACHED_VIA_OPTIONS)}")
    ws = connect()
    _, rows = fetch_all(ws)
    row_num, row = find_row(rows, args.company)
    update_cell(ws, row_num, "Reached Via", args.channel)
    print(f"{row[0]}: Reached Via -> {args.channel}")


def cmd_applied(args):
    ws = connect()
    _, rows = fetch_all(ws)
    row_num, row = find_row(rows, args.company)
    applied = args.date or date.today().strftime("%Y-%m-%d")
    try:
        datetime.strptime(applied, "%Y-%m-%d")
    except ValueError:
        sys.exit(f"Date must be YYYY-MM-DD, got '{applied}'")
    # Two writes batched manually via batch_update isn't needed — 2 calls is fine.
    update_cell(ws, row_num, "Status", "Submitted")
    update_cell(ws, row_num, "Date Applied", applied)
    print(f"{row[0]}: Submitted on {applied}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="show all applications").set_defaults(func=cmd_list)

    sp = sub.add_parser("show", help="show one row, all fields")
    sp.add_argument("company")
    sp.set_defaults(func=cmd_show)

    sp = sub.add_parser("status", help="set Status")
    sp.add_argument("company")
    sp.add_argument("status", choices=STATUS_OPTIONS)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("set", help="set any manual field")
    sp.add_argument("company")
    sp.add_argument("field")
    sp.add_argument("value")
    sp.set_defaults(func=cmd_set)

    sp = sub.add_parser("note", help="append timestamped note")
    sp.add_argument("company")
    sp.add_argument("text")
    sp.set_defaults(func=cmd_note)

    sp = sub.add_parser("link", help="set job posting URL")
    sp.add_argument("company")
    sp.add_argument("url")
    sp.set_defaults(func=cmd_link)

    sp = sub.add_parser("email", help="set recruiter/contact email")
    sp.add_argument("company")
    sp.add_argument("email")
    sp.set_defaults(func=cmd_email)

    sp = sub.add_parser("via", help="set how you reached them")
    sp.add_argument("company")
    sp.add_argument("channel", choices=REACHED_VIA_OPTIONS)
    sp.set_defaults(func=cmd_via)

    sp = sub.add_parser("applied", help="mark Submitted + set Date Applied")
    sp.add_argument("company")
    sp.add_argument("date", nargs="?", help="YYYY-MM-DD (default: today)")
    sp.set_defaults(func=cmd_applied)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
