#!/usr/bin/env python3
"""
Sync resumes/data/*.yml into the CV tracker Google Sheet.

- Upserts one row per company config, keyed on file stem.
- Refreshes only auto columns (Company, Role, Headline, Theme, HTML, PDF, Updated).
- Never touches manual columns (Status, Date Applied, Source, Contact, Next Action, Notes)
  on existing rows. New rows get Status="Drafted" as default.
- Total API ops per run: 1 read + at most 2 writes (well under 60/min quota).

Run setup_sheet.py once first to format the sheet.

Usage:
    python3 resumes/sync_tracker.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from gspread.utils import rowcol_to_a1

from sheet_common import (
    AUTO_COLS,
    DATA_DIR,
    HEADERS,
    MANUAL_COLS,
    OUTPUT_DIR,
    REPO_ROOT,
    get_or_create_ws,
    load_env,
    open_sheet,
)


def parse_role_from_header(yml_path: Path) -> str:
    """Header comment is usually '# Company - Role'. Pull text after the dash."""
    with yml_path.open() as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") and " - " in line:
                tail = line.lstrip("#").strip()
                if " - " in tail:
                    return tail.split(" - ", 1)[1].strip()
            elif line and not line.startswith("#"):
                break
    return ""


def collect_configs() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for yml in sorted(DATA_DIR.glob("*.yml")):
        if yml.stem == "base":
            continue
        try:
            data = yaml.safe_load(yml.read_text()) or {}
        except yaml.YAMLError as e:
            print(f"  skip {yml.name}: {e}")
            continue
        basics = data.get("basics") or {}
        theme = data.get("theme") or {}
        html_path = OUTPUT_DIR / f"{yml.stem}.html"
        pdf_path = OUTPUT_DIR / f"{yml.stem}.pdf"
        rows.append(
            {
                "Company": yml.stem,
                "Role": parse_role_from_header(yml),
                "Headline": basics.get("headline", ""),
                "Theme": theme.get("primary", ""),
                "HTML": str(html_path.relative_to(REPO_ROOT)) if html_path.exists() else "",
                "PDF": str(pdf_path.relative_to(REPO_ROOT)) if pdf_path.exists() else "",
                "Updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }
        )
    return rows


def main():
    env = load_env()
    configs = collect_configs()
    if not configs:
        sys.exit("No company configs found in resumes/data/")
    print(f"Found {len(configs)} configs: {', '.join(c['Company'] for c in configs)}")

    sh = open_sheet(env)
    ws = get_or_create_ws(sh, env["GOOGLE_SHEET_TAB"], cols=len(HEADERS) + 2, rows=200)
    print(f"Tab: {ws.title}")

    # 1 read
    existing = ws.get_all_values()
    if not existing or existing[0][: len(HEADERS)] != HEADERS:
        # No proper header — write it, no manual data to preserve
        ws.update(range_name=f"A1:{rowcol_to_a1(1, len(HEADERS))}", values=[HEADERS])
        existing = [HEADERS]

    row_by_company = {
        row[0]: i for i, row in enumerate(existing[1:], start=2) if row and row[0]
    }

    updates: list[dict] = []
    appends: list[list[str]] = []

    for cfg in configs:
        auto_values = [cfg[col] for col in AUTO_COLS]
        if cfg["Company"] in row_by_company:
            row_num = row_by_company[cfg["Company"]]
            rng = f"A{row_num}:{rowcol_to_a1(row_num, len(AUTO_COLS))}"
            updates.append({"range": rng, "values": [auto_values]})
        else:
            manual = [""] * len(MANUAL_COLS)
            manual[MANUAL_COLS.index("Status")] = "Drafted"
            appends.append(auto_values + manual)

    # 1 batched write for updates
    if updates:
        ws.batch_update(updates, value_input_option="USER_ENTERED")
        print(f"Updated {len(updates)} existing rows")

    # 1 append for new rows
    if appends:
        ws.append_rows(appends, value_input_option="USER_ENTERED")
        print(f"Appended {len(appends)} new rows: {[a[0] for a in appends]}")

    if not updates and not appends:
        print("Nothing to sync")

    print(f"\nSheet: https://docs.google.com/spreadsheets/d/{env['GOOGLE_SHEET_ID']}/edit")


if __name__ == "__main__":
    main()
