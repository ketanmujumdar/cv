#!/usr/bin/env python3
"""
Interactive resume picker.

Lists company configs in resumes/data/, lets you choose one, then choose an
action (build HTML, build HTML+PDF, serve with live reload).

Usage:
    python3 resumes/pick.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"


def list_companies() -> list[str]:
    return sorted(
        c.stem for c in DATA_DIR.glob("*.yml") if c.stem != "base"
    )


def prompt_choice(label: str, options: list[str], default: int = 1) -> int:
    print(f"\n{label}")
    for i, opt in enumerate(options, 1):
        marker = " *" if i == default else "  "
        print(f"  {marker}{i}. {opt}")
    while True:
        raw = input(f"\nChoice [1-{len(options)}] (default {default}): ").strip()
        if not raw:
            return default
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(options):
                return n
        print("  Invalid choice. Try again.")


def main():
    companies = list_companies()
    if not companies:
        sys.exit("No company configs found in resumes/data/.")

    print("Resume Picker")
    print("=" * 40)
    company_idx = prompt_choice("Select company:", companies, default=len(companies))
    company = companies[company_idx - 1]

    actions = [
        "Build HTML",
        "Build HTML + PDF",
        "Serve with live reload (HTML)",
        "Serve with live reload (HTML + PDF)",
    ]
    action_idx = prompt_choice("Select action:", actions, default=2)

    if action_idx == 1:
        cmd = [sys.executable, str(ROOT / "build.py"), company]
    elif action_idx == 2:
        cmd = [sys.executable, str(ROOT / "build.py"), company, "--pdf"]
    elif action_idx == 3:
        cmd = [sys.executable, str(ROOT / "serve.py"), company]
    else:
        cmd = [sys.executable, str(ROOT / "serve.py"), company, "--pdf"]

    print(f"\nRunning: {' '.join(cmd)}\n")
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
