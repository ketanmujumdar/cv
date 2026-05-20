#!/usr/bin/env bash
#
# rx-resume.sh — CLI wrapper for RX Resume API
#
# Usage:
#   ./rx-resume.sh list                          List all resumes
#   ./rx-resume.sh get <id>                      Get full resume data
#   ./rx-resume.sh get <id> --pretty             Get resume, pretty printed
#   ./rx-resume.sh duplicate <id> <name> <slug>  Duplicate a resume
#   ./rx-resume.sh update <id> <json-file>       Update resume from JSON file
#   ./rx-resume.sh patch <id> <path> <value>     Patch a single field
#   ./rx-resume.sh pdf <id> <output-file>        Download resume as PDF
#   ./rx-resume.sh delete <id>                   Delete a resume
#   ./rx-resume.sh snapshot <id> [dir]           Save a timestamped JSON snapshot
#   ./rx-resume.sh health                        Check API health
#
# Environment:
#   RX_RESUME_API_KEY  — required, your API key from rxresu.me Settings → API Keys
#
# Examples:
#   export RX_RESUME_API_KEY="your-key-here"
#   ./rx-resume.sh list
#   ./rx-resume.sh snapshot 019e4450-cabb-7389-b242-cb04093a51db ./snapshots
#

set -euo pipefail

BASE_URL="https://rxresu.me/api/openapi"
HEALTH_URL="https://rxresu.me/api/health"

# --- Helpers ---

die() { echo "ERROR: $*" >&2; exit 1; }

require_key() {
  [[ -n "${RX_RESUME_API_KEY:-}" ]] || die "RX_RESUME_API_KEY not set. Export it first."
}

api() {
  local method="$1" path="$2"
  shift 2
  curl -s -X "$method" "${BASE_URL}${path}" \
    -H "x-api-key: ${RX_RESUME_API_KEY}" \
    -H "Content-Type: application/json" \
    "$@"
}

pretty() {
  python3 -m json.tool 2>/dev/null || cat
}

# --- Commands ---

cmd_health() {
  curl -s "$HEALTH_URL" | pretty
}

cmd_list() {
  require_key
  api GET "/resumes" | python3 -c "
import sys, json
resumes = json.load(sys.stdin)
if not resumes:
    print('No resumes found.')
    sys.exit(0)
print(f'{'ID':<40} {'Name':<40} {'Updated'}')
print('-' * 100)
for r in resumes:
    print(f'{r[\"id\"]:<40} {r[\"name\"]:<40} {r[\"updatedAt\"][:10]}')
" 2>/dev/null || api GET "/resumes" | pretty
}

cmd_get() {
  require_key
  local id="$1"
  local output
  output=$(api GET "/resumes/${id}")
  if [[ "${2:-}" == "--pretty" ]]; then
    echo "$output" | pretty
  else
    echo "$output"
  fi
}

cmd_duplicate() {
  require_key
  local id="$1" name="$2" slug="$3"
  local result
  result=$(api POST "/resumes/${id}/duplicate" -d "{\"name\": \"${name}\", \"slug\": \"${slug}\", \"tags\": []}")
  echo "Duplicated resume. New ID: ${result}"
}

cmd_update() {
  require_key
  local id="$1" json_file="$2"
  [[ -f "$json_file" ]] || die "File not found: $json_file"
  api PUT "/resumes/${id}" -d "@${json_file}" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Updated: {d.get(\"name\", \"unknown\")}')
print(f'ID: {d.get(\"id\", \"unknown\")}')
print(f'Updated at: {d.get(\"updatedAt\", \"\")}')
exp = d.get('data', {}).get('sections', {}).get('experience', {}).get('items', [])
print(f'Experience entries: {len(exp)}')
skills = d.get('data', {}).get('sections', {}).get('skills', {}).get('items', [])
print(f'Skill entries: {len(skills)}')
" 2>/dev/null || echo "Update sent."
}

cmd_patch() {
  require_key
  local id="$1" path="$2" value="$3"
  api PATCH "/resumes/${id}" \
    -d "{\"operations\": [{\"op\": \"replace\", \"path\": \"${path}\", \"value\": \"${value}\"}]}" | pretty
}

cmd_pdf() {
  require_key
  local id="$1" output="${2:-resume.pdf}"
  curl -s "${BASE_URL}/resumes/${id}/pdf" \
    -H "x-api-key: ${RX_RESUME_API_KEY}" \
    -o "$output"
  echo "PDF saved to: $output"
}

cmd_delete() {
  require_key
  local id="$1"
  read -rp "Delete resume ${id}? (y/N) " confirm
  [[ "$confirm" == "y" || "$confirm" == "Y" ]] || die "Aborted."
  api DELETE "/resumes/${id}"
  echo "Deleted."
}

cmd_snapshot() {
  require_key
  local id="$1"
  local dir="${2:-./snapshots}"
  mkdir -p "$dir"
  local data
  data=$(api GET "/resumes/${id}")
  local name timestamp filename
  name=$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','unknown'))" 2>/dev/null)
  timestamp=$(date +%Y%m%d_%H%M%S)
  filename="${dir}/${name}_${timestamp}.json"
  echo "$data" | python3 -m json.tool > "$filename" 2>/dev/null || echo "$data" > "$filename"
  echo "Snapshot saved: $filename"
}

# --- Main ---

usage() {
  echo "Usage: $0 <command> [args]"
  echo ""
  echo "Commands:"
  echo "  health                          Check API health"
  echo "  list                            List all resumes"
  echo "  get <id> [--pretty]             Get full resume data"
  echo "  duplicate <id> <name> <slug>    Duplicate a resume"
  echo "  update <id> <json-file>         Update resume from JSON file"
  echo "  patch <id> <path> <value>       Patch a single field"
  echo "  pdf <id> <output-file>          Download as PDF"
  echo "  delete <id>                     Delete a resume"
  echo "  snapshot <id> [dir]             Save timestamped JSON snapshot"
  echo ""
  echo "Environment: RX_RESUME_API_KEY must be set."
  exit 1
}

[[ $# -ge 1 ]] || usage

case "$1" in
  health)    cmd_health ;;
  list)      cmd_list ;;
  get)       [[ $# -ge 2 ]] || die "Usage: $0 get <id> [--pretty]"; cmd_get "$2" "${3:-}" ;;
  duplicate) [[ $# -ge 4 ]] || die "Usage: $0 duplicate <id> <name> <slug>"; cmd_duplicate "$2" "$3" "$4" ;;
  update)    [[ $# -ge 3 ]] || die "Usage: $0 update <id> <json-file>"; cmd_update "$2" "$3" ;;
  patch)     [[ $# -ge 4 ]] || die "Usage: $0 patch <id> <path> <value>"; cmd_patch "$2" "$3" "$4" ;;
  pdf)       [[ $# -ge 2 ]] || die "Usage: $0 pdf <id> [output-file]"; cmd_pdf "$2" "${3:-}" ;;
  delete)    [[ $# -ge 2 ]] || die "Usage: $0 delete <id>"; cmd_delete "$2" ;;
  snapshot)  [[ $# -ge 2 ]] || die "Usage: $0 snapshot <id> [dir]"; cmd_snapshot "$2" "${3:-}" ;;
  *)         die "Unknown command: $1. Run $0 without args for usage." ;;
esac
