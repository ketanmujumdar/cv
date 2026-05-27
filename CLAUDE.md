# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jekyll-based online CV/resume for Ketan Mujumdar, hosted on GitHub Pages. Based on the [webjeda online-cv](https://github.com/sharu725/online-cv) theme.

## Development Commands

```bash
# Local development with Ruby/Jekyll
bundle install
bundle exec jekyll serve

# Local development with Docker
docker-compose up
```

Site runs at `http://localhost:4000`. Theme skin changes require a restart.

## Architecture

All CV content lives in a single file: `_data/data.yml`. This is the primary file to edit when updating resume content (roles, education, skills, sidebar info, etc.). Be careful with YAML syntax — even small errors break the build.

**Layouts:**
- `_layouts/default.html` — main page (sidebar + content wrapper)
- `_layouts/print.html` — print-friendly version at `/print`
- `_layouts/compress.html` — HTML minification

**Pages:**
- `index.html` — assembles sections via `{% include %}` tags
- `print.html` — same sections, print layout

**Sections** (`_includes/`): `career-profile`, `experiences`, `education`, `skills`, `projects`, `publications`, `sidebar`, `contact`, `language`, `interests`. Each reads from `site.data.data`.

**Styling:**
- Theme skin set via `theme_skin` in `_config.yml` (options: blue, turquoise, green, berry, orange, ceramic)
- Skin SCSS files in `_sass/skins/`, base styles in `_sass/_base.scss`
- `assets/css/main.scss` imports the active skin + defaults

**Sidebar education toggle:** `sidebar.education: True` in `data.yml` puts education in sidebar; `False` moves it to main content area.

## Writing Rules

- Never use em dashes (—) anywhere in resume content, data files, or generated output. Use hyphens (-), commas, or rewrite the sentence instead.

## Resume Builder (resumes/)

Standalone HTML resume system for tailoring resumes per company. No external dependencies for HTML; PDF export requires Playwright.

```bash
# Prerequisites (one-time)
pip3 install pyyaml jinja2

# Optional: PDF export via Playwright
pip3 install playwright && playwright install chromium
```

### build.py — one-shot builder

```bash
# Build HTML for a company
python3 resumes/build.py flo_energy

# Build all company configs
python3 resumes/build.py --all

# Also export PDF (requires Playwright)
python3 resumes/build.py flo_energy --pdf

# List available company configs
python3 resumes/build.py --list
```

Output goes to `resumes/output/<company>.html` (and `.pdf` if requested).

### serve.py — dev server with live reload

```bash
# Build + serve + open browser, watch for changes
python3 resumes/serve.py flo_energy

# Also export PDF on build and on every file change
python3 resumes/serve.py flo_energy --pdf

# Custom port
python3 resumes/serve.py flo_energy --port 9000

# Build + serve all configs
python3 resumes/serve.py --all
```

Serves `resumes/output/` at `http://localhost:8080`. Watches `resumes/data/` and `resumes/templates/` — any change triggers an automatic rebuild. Refresh the browser to see updates.

**How it works:**
- `resumes/data/base.yml` has shared profile data (contact, experience, skills, education)
- `resumes/data/<company>.yml` overrides specific fields (headline, summary, skill emphasis, cover letter)
- `resumes/templates/modern.html` is the Jinja2 HTML+CSS template
- `resumes/build.py` merges base + company data and renders to `resumes/output/<company>.html`

**To add a new company:** copy `resumes/data/sonar.yml` to `resumes/data/newcompany.yml`, edit the overrides, run `python3 resumes/serve.py newcompany`.

## Deployment

Pushes to `master` auto-deploy via GitHub Pages. Custom domain: `online-cv.webjeda.com` (CNAME file).
