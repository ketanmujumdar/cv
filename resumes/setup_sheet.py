#!/usr/bin/env python3
"""
One-time setup for the CV tracker Google Sheet.

Creates and formats:
- Applications tab: header band, frozen header + first column, banded rows,
  Status dropdown + colored conditional formatting, auto-sized columns.
- Dashboard tab: live counts of applications by status (formula-driven).

Safe to re-run — it clears prior banding + conditional rules first to avoid
duplicates. Idempotent.

Usage:
    python3 resumes/setup_sheet.py
"""

from __future__ import annotations

import sys

from gspread.utils import rowcol_to_a1

from sheet_common import (
    AUTO_COLS,
    HEADERS,
    MANUAL_COLS,
    REACHED_VIA_OPTIONS,
    STATUS_OPTIONS,
    get_or_create_ws,
    hex_to_rgb,
    load_env,
    open_sheet,
)

STATUS_COLORS = {
    "Drafted":   "#f3f4f6",
    "Submitted": "#dbeafe",
    "Screening": "#fde68a",
    "Interview": "#fbcfe8",
    "Offer":     "#bbf7d0",
    "Rejected":  "#fecaca",
    "Withdrawn": "#e5e7eb",
}


def setup_applications_tab(sh, ws) -> None:
    """Fancy formatting on the Applications tab. One batched request."""
    sheet_id = ws.id
    end_col = len(HEADERS)

    # Write header row first (single .update call)
    current = ws.get_all_values()
    if not current or current[0][: len(HEADERS)] != HEADERS:
        ws.update(
            range_name=f"A1:{rowcol_to_a1(1, len(HEADERS))}",
            values=[HEADERS],
        )

    header_range = {
        "sheetId": sheet_id,
        "startRowIndex": 0,
        "endRowIndex": 1,
        "startColumnIndex": 0,
        "endColumnIndex": end_col,
    }
    body_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "startColumnIndex": 0,
        "endColumnIndex": end_col,
    }
    status_col_idx = HEADERS.index("Status")
    status_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "endRowIndex": 1000,
        "startColumnIndex": status_col_idx,
        "endColumnIndex": status_col_idx + 1,
    }
    date_col_idx = HEADERS.index("Date Applied")
    date_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "endRowIndex": 1000,
        "startColumnIndex": date_col_idx,
        "endColumnIndex": date_col_idx + 1,
    }
    reached_col_idx = HEADERS.index("Reached Via")
    reached_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "endRowIndex": 1000,
        "startColumnIndex": reached_col_idx,
        "endColumnIndex": reached_col_idx + 1,
    }
    link_col_idx = HEADERS.index("Link")
    link_range = {
        "sheetId": sheet_id,
        "startRowIndex": 1,
        "endRowIndex": 1000,
        "startColumnIndex": link_col_idx,
        "endColumnIndex": link_col_idx + 1,
    }

    # Delete existing banding + conditional rules so re-runs stay clean
    cleanup: list[dict] = []
    try:
        meta = sh.fetch_sheet_metadata(
            params={"fields": "sheets(properties.sheetId,bandedRanges.bandedRangeId,conditionalFormats)"}
        )
        for sheet in meta.get("sheets", []):
            if sheet["properties"]["sheetId"] != sheet_id:
                continue
            for band in sheet.get("bandedRanges", []) or []:
                cleanup.append({"deleteBanding": {"bandedRangeId": band["bandedRangeId"]}})
            cf_count = len(sheet.get("conditionalFormats", []) or [])
            for i in range(cf_count - 1, -1, -1):
                cleanup.append({"deleteConditionalFormatRule": {"sheetId": sheet_id, "index": i}})
    except Exception as e:
        print(f"  (cleanup skipped: {e})")

    requests: list[dict] = list(cleanup) + [
        # Header band
        {
            "repeatCell": {
                "range": header_range,
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": hex_to_rgb("#0F172A"),
                        "horizontalAlignment": "LEFT",
                        "verticalAlignment": "MIDDLE",
                        "padding": {"top": 10, "right": 12, "bottom": 10, "left": 12},
                        "textFormat": {
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            "fontFamily": "Inter",
                            "fontSize": 11,
                            "bold": True,
                        },
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,padding,textFormat)",
            }
        },
        # Body cells
        {
            "repeatCell": {
                "range": body_range,
                "cell": {
                    "userEnteredFormat": {
                        "verticalAlignment": "MIDDLE",
                        "wrapStrategy": "WRAP",
                        "padding": {"top": 6, "right": 10, "bottom": 6, "left": 10},
                        "textFormat": {"fontFamily": "Inter", "fontSize": 10},
                    }
                },
                "fields": "userEnteredFormat(verticalAlignment,wrapStrategy,padding,textFormat)",
            }
        },
        # Date column number format
        {
            "repeatCell": {
                "range": date_range,
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": {"type": "DATE", "pattern": "yyyy-mm-dd"}
                    }
                },
                "fields": "userEnteredFormat.numberFormat",
            }
        },
        # Freeze header + first column
        {
            "updateSheetProperties": {
                "properties": {
                    "sheetId": sheet_id,
                    "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 1},
                },
                "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
            }
        },
        # Auto-resize columns
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": end_col,
                }
            }
        },
        # Increase row height for body
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": 1,
                    "endIndex": 200,
                },
                "properties": {"pixelSize": 36},
                "fields": "pixelSize",
            }
        },
        # Status dropdown
        {
            "setDataValidation": {
                "range": status_range,
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": s} for s in STATUS_OPTIONS],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        },
        # Reached Via dropdown
        {
            "setDataValidation": {
                "range": reached_range,
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [{"userEnteredValue": v} for v in REACHED_VIA_OPTIONS],
                    },
                    "showCustomUi": True,
                    "strict": False,
                },
            }
        },
        # Link column: URL validation (turns into hyperlink + warning if invalid)
        {
            "setDataValidation": {
                "range": link_range,
                "rule": {
                    "condition": {"type": "TEXT_IS_URL"},
                    "showCustomUi": False,
                    "strict": False,
                },
            }
        },
        # Banded rows
        {
            "addBanding": {
                "bandedRange": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "startColumnIndex": 0,
                        "endColumnIndex": end_col,
                    },
                    "rowProperties": {
                        "headerColor": hex_to_rgb("#0F172A"),
                        "firstBandColor": {"red": 1, "green": 1, "blue": 1},
                        "secondBandColor": hex_to_rgb("#f8fafc"),
                    },
                }
            }
        },
    ]

    # Conditional format per status (added last, in display order)
    for status, color in STATUS_COLORS.items():
        requests.append(
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [status_range],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": status}],
                            },
                            "format": {
                                "backgroundColor": hex_to_rgb(color),
                                "textFormat": {"bold": True},
                            },
                        },
                    },
                    "index": 0,
                }
            }
        )

    sh.batch_update({"requests": requests})


def setup_dashboard_tab(sh, applications_tab_name: str) -> None:
    """Tiny dashboard: counts of applications per status."""
    ws = get_or_create_ws(sh, "Dashboard", cols=4, rows=30)
    sheet_id = ws.id

    rows: list[list[str]] = [
        ["CV Application Tracker"],
        [""],
        ["Status", "Count"],
    ]
    for status in STATUS_OPTIONS:
        rows.append(
            [status, f'=COUNTIF(\'{applications_tab_name}\'!H2:H1000,"{status}")']
        )
    rows.append(["Total", f'=COUNTA(\'{applications_tab_name}\'!A2:A1000)'])

    ws.update(range_name="A1", values=rows, value_input_option="USER_ENTERED")

    requests = [
        # Title
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": hex_to_rgb("#0F172A"),
                        "horizontalAlignment": "LEFT",
                        "padding": {"top": 10, "right": 12, "bottom": 10, "left": 12},
                        "textFormat": {
                            "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            "fontFamily": "Inter",
                            "fontSize": 14,
                            "bold": True,
                        },
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,padding,textFormat)",
            }
        },
        # Header row for the count table
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 2,
                    "endRowIndex": 3,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": hex_to_rgb("#e2e8f0"),
                        "padding": {"top": 6, "right": 10, "bottom": 6, "left": 10},
                        "textFormat": {
                            "fontFamily": "Inter",
                            "fontSize": 11,
                            "bold": True,
                        },
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,padding,textFormat)",
            }
        },
        # Body
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 3,
                    "endRowIndex": 3 + len(STATUS_OPTIONS) + 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                "cell": {
                    "userEnteredFormat": {
                        "padding": {"top": 6, "right": 10, "bottom": 6, "left": 10},
                        "textFormat": {"fontFamily": "Inter", "fontSize": 10},
                    }
                },
                "fields": "userEnteredFormat(padding,textFormat)",
            }
        },
        # Merge title row
        {
            "mergeCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                "mergeType": "MERGE_ALL",
            }
        },
        # Auto-resize
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 2,
                }
            }
        },
    ]
    sh.batch_update({"requests": requests})


def main():
    env = load_env()
    sh = open_sheet(env)
    applications_tab = env["GOOGLE_SHEET_TAB"]

    ws = get_or_create_ws(sh, applications_tab, cols=len(HEADERS) + 2, rows=200)
    print(f"Setting up tab: {applications_tab}")
    setup_applications_tab(sh, ws)
    print("  done")

    print("Setting up Dashboard tab")
    setup_dashboard_tab(sh, applications_tab)
    print("  done")

    print(f"\nSheet: https://docs.google.com/spreadsheets/d/{env['GOOGLE_SHEET_ID']}/edit")
    print("Next: python3 resumes/sync_tracker.py")


if __name__ == "__main__":
    main()
