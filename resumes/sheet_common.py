"""Shared helpers for setup_sheet.py and sync_tracker.py."""

from __future__ import annotations

import sys
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "resumes" / "data"
OUTPUT_DIR = REPO_ROOT / "resumes" / "output"
ENV_FILE = REPO_ROOT / "resumes" / ".env"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

AUTO_COLS = ["Company", "Role", "Headline", "Theme", "HTML", "PDF", "Updated"]
MANUAL_COLS = [
    "Status",
    "Date Applied",
    "Source",
    "Contact",
    "Next Action",
    "Notes",
    "Link",
    "Email",
    "Reached Via",
]
HEADERS = AUTO_COLS + MANUAL_COLS

STATUS_OPTIONS = [
    "Drafted",
    "Submitted",
    "Screening",
    "Interview",
    "Offer",
    "Rejected",
    "Withdrawn",
]

REACHED_VIA_OPTIONS = [
    "LinkedIn",
    "Email",
    "Referral",
    "Portal",
    "Recruiter",
    "Cold outreach",
    "Other",
]


def load_env() -> dict[str, str]:
    if not ENV_FILE.exists():
        sys.exit(f"Missing {ENV_FILE}. Copy resumes/.env.example to resumes/.env first.")
    env: dict[str, str] = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    for key in ("GOOGLE_SHEET_ID", "GOOGLE_CREDS_PATH"):
        if not env.get(key):
            sys.exit(f"{key} missing from {ENV_FILE}")
    env.setdefault("GOOGLE_SHEET_TAB", "Applications")
    return env


def open_sheet(env: dict[str, str]):
    creds_path = REPO_ROOT / env["GOOGLE_CREDS_PATH"]
    if not creds_path.exists():
        sys.exit(f"Credentials not found: {creds_path}")
    creds = Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_key(env["GOOGLE_SHEET_ID"])
    return sh


def get_or_create_ws(sh, title: str, cols: int = 20, rows: int = 200):
    try:
        return sh.worksheet(title)
    except gspread.WorksheetNotFound:
        return sh.add_worksheet(title=title, rows=rows, cols=cols)


def hex_to_rgb(hex_str: str) -> dict[str, float]:
    s = hex_str.lstrip("#")
    if len(s) != 6:
        return {"red": 0.95, "green": 0.95, "blue": 0.95}
    return {
        "red": int(s[0:2], 16) / 255,
        "green": int(s[2:4], 16) / 255,
        "blue": int(s[4:6], 16) / 255,
    }
