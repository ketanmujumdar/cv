#!/usr/bin/env python3
"""
Resume dev server — builds a resume and serves output/ with live-reload on file changes.

Usage:
    python serve.py flo_energy          # Build + serve, watch for changes
    python serve.py flo_energy --pdf    # Build + export PDF + serve
    python serve.py flo_energy --port 9000
    python serve.py --all               # Build all, serve output/
"""

import argparse
import http.server
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

from build import DATA_DIR, OUTPUT_DIR, build, generate_pdf, list_companies, load_data

ROOT = Path(__file__).parent
WATCH_DIRS = [DATA_DIR, ROOT / "templates"]


def get_mtimes():
    mtimes = {}
    for d in WATCH_DIRS:
        for f in d.rglob("*"):
            if f.is_file():
                mtimes[f] = f.stat().st_mtime
    return mtimes


def export_pdf(company: str):
    html_path = OUTPUT_DIR / f"{company}.html"
    pdf_path = OUTPUT_DIR / f"{company}.pdf"
    data = load_data(company)
    name = (data.get("basics") or {}).get("name", "")
    sidebar_bg = (data.get("theme") or {}).get("sidebar_bg", "#f8fafc")
    generate_pdf(html_path, pdf_path, name, sidebar_bg)


def watch(company: str, template: str, pdf: bool = False, interval: float = 1.0):
    print(f"Watching {', '.join(str(d) for d in WATCH_DIRS)} for changes...")
    known = get_mtimes()
    while True:
        time.sleep(interval)
        current = get_mtimes()
        changed = [f for f, t in current.items() if known.get(f) != t]
        changed += [f for f in known if f not in current]
        if changed:
            print(f"\nChanged: {[str(f) for f in changed]}")
            try:
                if company == "__all__":
                    for config in sorted(DATA_DIR.glob("*.yml")):
                        if config.stem != "base":
                            build(config.stem, template)
                            if pdf:
                                export_pdf(config.stem)
                else:
                    build(company, template)
                    if pdf:
                        export_pdf(company)
                print("Rebuilt. Refresh your browser.")
            except Exception as e:
                print(f"Build error: {e}")
            known = get_mtimes()


def serve(port: int, open_path: str):
    os.chdir(OUTPUT_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    handler.log_message = lambda *a: None  # suppress request logs

    with http.server.HTTPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/{open_path}"
        print(f"Serving at {url}")
        webbrowser.open(url)
        httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Build + serve resumes with live reload")
    parser.add_argument("company", nargs="?", help="Company config name (e.g. flo_energy)")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--template", default="modern")
    parser.add_argument("--pdf", action="store_true", help="Also export PDF (and re-export on changes)")
    parser.add_argument("--all", action="store_true", help="Build all configs")
    parser.add_argument("--list", action="store_true", help="List available configs")
    args = parser.parse_args()

    if args.list:
        list_companies()
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    if args.all:
        for config in sorted(DATA_DIR.glob("*.yml")):
            if config.stem != "base":
                build(config.stem, args.template)
                if args.pdf:
                    export_pdf(config.stem)
        open_path = ""
        watch_target = "__all__"
    elif args.company:
        build(args.company, args.template)
        if args.pdf:
            export_pdf(args.company)
        open_path = f"{args.company}.html"
        watch_target = args.company
    else:
        parser.print_help()
        sys.exit(1)

    watcher = threading.Thread(target=watch, args=(watch_target, args.template, args.pdf), daemon=True)
    watcher.start()

    serve(args.port, open_path)


if __name__ == "__main__":
    main()
