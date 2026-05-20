#!/usr/bin/env python3
"""
Resume builder — merges base data with company-specific overrides,
renders an HTML resume from a Jinja2 template, and optionally generates a PDF.

Usage:
    python build.py sonar                    # Build HTML only
    python build.py sonar --pdf              # Build HTML + PDF (requires Playwright)
    python build.py sonar --template fancy   # Use a different template
    python build.py --list                   # List available company configs
    python build.py --all                    # Build all company configs
"""

import argparse
import copy
import os
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Override wins for scalars."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_data(company: str) -> dict:
    """Load base.yml and merge with company-specific overrides."""
    base_path = DATA_DIR / "base.yml"
    company_path = DATA_DIR / f"{company}.yml"

    if not base_path.exists():
        sys.exit(f"Error: base data not found at {base_path}")
    if not company_path.exists():
        sys.exit(f"Error: company config not found at {company_path}")

    with open(base_path) as f:
        base = yaml.safe_load(f)
    with open(company_path) as f:
        company_data = yaml.safe_load(f) or {}

    return deep_merge(base, company_data)


def render_html(data: dict, template_name: str = "modern") -> str:
    """Render a resume HTML from template + data."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,
    )
    template = env.get_template(f"{template_name}.html")
    return template.render(**data)


def generate_pdf(html_path: Path, pdf_path: Path):
    """Generate PDF from HTML using Playwright."""
    script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
    const browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto('file://{html_path.resolve()}', {{ waitUntil: 'networkidle' }});
    await page.pdf({{
        path: '{pdf_path.resolve()}',
        format: 'A4',
        printBackground: true,
        margin: {{ top: '0mm', right: '0mm', bottom: '0mm', left: '0mm' }}
    }});
    await browser.close();
}})();
"""
    # Try Node.js + Playwright first
    try:
        result = subprocess.run(
            ["node", "-e", script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print(f"  PDF: {pdf_path}")
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: try Python playwright
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{html_path.resolve()}", wait_until="networkidle")
            page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
            )
            browser.close()
        print(f"  PDF: {pdf_path}")
        return
    except ImportError:
        pass

    print("  PDF skipped: install 'playwright' (npm or pip) for PDF generation.")
    print(f"  Alternatively, open {html_path} in a browser and print to PDF.")


def list_companies():
    """List available company configs."""
    configs = sorted(DATA_DIR.glob("*.yml"))
    print("Available company configs:")
    for c in configs:
        if c.stem == "base":
            continue
        print(f"  - {c.stem}")


def build(company: str, template: str = "modern", pdf: bool = False):
    """Build HTML (and optionally PDF) for a company."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Building: {company}")
    data = load_data(company)
    html = render_html(data, template)

    html_path = OUTPUT_DIR / f"{company}.html"
    html_path.write_text(html)
    print(f"  HTML: {html_path}")

    if pdf:
        pdf_path = OUTPUT_DIR / f"{company}.pdf"
        generate_pdf(html_path, pdf_path)


def main():
    parser = argparse.ArgumentParser(description="Build tailored resumes")
    parser.add_argument("company", nargs="?", help="Company config name (e.g. sonar)")
    parser.add_argument("--template", default="modern", help="Template name (default: modern)")
    parser.add_argument("--pdf", action="store_true", help="Also generate PDF")
    parser.add_argument("--list", action="store_true", help="List available company configs")
    parser.add_argument("--all", action="store_true", help="Build all company configs")
    args = parser.parse_args()

    if args.list:
        list_companies()
        return

    if args.all:
        for config in sorted(DATA_DIR.glob("*.yml")):
            if config.stem == "base":
                continue
            build(config.stem, args.template, args.pdf)
        return

    if not args.company:
        parser.print_help()
        return

    build(args.company, args.template, args.pdf)


if __name__ == "__main__":
    main()
