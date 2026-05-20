# RX Resume API Reference

Base URL: `https://rxresu.me/api/openapi`

## Authentication

All authenticated endpoints require the `x-api-key` header.

```
x-api-key: <YOUR_API_KEY>
```

API keys are created at: https://rxresu.me → Settings → API Keys

> **Note:** The OpenAPI spec is available at `https://rxresu.me/api/openapi/spec.json`

## Health Check

```bash
curl -s "https://rxresu.me/api/health"
```

No auth required. Returns service status, database health, and storage health.

## Resume Endpoints

### List All Resumes

```bash
curl -s "https://rxresu.me/api/openapi/resumes" \
  -H "x-api-key: $RX_RESUME_API_KEY"
```

Returns metadata only (no full data). Supports query params:
- `tags` — filter by tags (array)
- `sort` — `lastUpdatedAt`, `createdAt`, `name`

### Get Single Resume (Full Data)

```bash
curl -s "https://rxresu.me/api/openapi/resumes/{id}" \
  -H "x-api-key: $RX_RESUME_API_KEY"
```

Returns complete resume including all sections, metadata, and design settings.

### Create Resume

```bash
curl -s -X POST "https://rxresu.me/api/openapi/resumes" \
  -H "x-api-key: $RX_RESUME_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Resume Name", "slug": "resume-slug", "tags": [], "withSampleData": false}'
```

### Update Resume (Full)

```bash
curl -s -X PUT "https://rxresu.me/api/openapi/resumes/{id}" \
  -H "x-api-key: $RX_RESUME_API_KEY" \
  -H "Content-Type: application/json" \
  -d @resume_data.json
```

Body fields (all optional): `name`, `slug`, `tags`, `data`, `isPublic`

### Patch Resume (JSON Patch - RFC 6902)

```bash
curl -s -X PATCH "https://rxresu.me/api/openapi/resumes/{id}" \
  -H "x-api-key: $RX_RESUME_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operations": [{"op": "replace", "path": "/basics/name", "value": "New Name"}]}'
```

Useful for targeted updates without sending the entire resume object.

### Duplicate Resume

```bash
curl -s -X POST "https://rxresu.me/api/openapi/resumes/{id}/duplicate" \
  -H "x-api-key: $RX_RESUME_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Copy Name", "slug": "copy-slug", "tags": []}'
```

**Important:** The `tags` field is required (even if empty array), otherwise you get a 400 error.

### Delete Resume

```bash
curl -s -X DELETE "https://rxresu.me/api/openapi/resumes/{id}" \
  -H "x-api-key: $RX_RESUME_API_KEY"
```

### Lock/Unlock Resume

```bash
curl -s -X POST "https://rxresu.me/api/openapi/resumes/{id}/lock" \
  -H "x-api-key: $RX_RESUME_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"isLocked": true}'
```

### Download PDF

```bash
curl -s "https://rxresu.me/api/openapi/resumes/{id}/pdf" \
  -H "x-api-key: $RX_RESUME_API_KEY" \
  -o resume.pdf
```

### Import Resume

```bash
curl -s -X POST "https://rxresu.me/api/openapi/resumes/import" \
  -H "x-api-key: $RX_RESUME_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data": { ... }}'
```

## Sharing Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/resumes/{username}/{slug}` | No | Get public resume |
| PUT | `/resumes/{id}/password` | Yes | Set password |
| DELETE | `/resumes/{id}/password` | Yes | Remove password |

## Other Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/resumes/tags` | Yes | List all tags |
| GET | `/resumes/{id}/statistics` | Yes | View/download stats |
| GET | `/resumes/{id}/analysis` | Yes | Get AI analysis |
| DELETE | `/auth/account` | Yes | Delete account |

## Resume Data Structure

The `data` field in a resume follows this structure:

```
data
├── picture         — avatar settings (url, size, border, etc.)
├── basics          — name, headline, email, phone, location, website
├── summary         — title, content (HTML), columns, hidden
└── sections
    ├── profiles    — LinkedIn, GitHub, etc.
    ├── experience  — company, position, period, description (HTML)
    ├── education   — school, degree, area, period
    ├── skills      — name, level, keywords[]
    ├── projects    — name, description, keywords
    ├── languages   — language, fluency, level
    ├── interests   — name, keywords
    ├── awards      — title, awarder, date
    ├── certifications — name, issuer, date
    ├── publications — name, publisher, date
    ├── volunteer   — organization, position, period
    └── references  — name, description
```

Each section has: `title`, `columns`, `hidden`, `items[]`
Each item has: `id`, `hidden`, plus section-specific fields.
Descriptions use HTML format (wrap in `<ul><li><p>...</p></li></ul>`).
