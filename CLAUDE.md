# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Aphasia therapy platform with a FastAPI backend, Next.js frontend, and Supabase (PostgreSQL) database. This is a **production application** used by speech-language pathologists and patients to store sensitive personal health information and treatment progress. Security is a critical concern in all development.

## Critical Guidelines

### Thin Client Architecture
**Do not add business logic to the frontend.** This project follows a strict thin client architecture where as much logic as possible is handled on the backend. The frontend should only handle UI rendering, user interactions, and API calls. All validation, data processing, calculations, and business rules must be implemented in the backend.

### DRY (Don't Repeat Yourself)
**Extract shared logic into reusable utilities.** Backend shared helpers live in `backend/app/services/utils.py` (ownership verification, session verification, update building, soft deletion, entity listing, storage uploads, `FRONTEND_URL`). Frontend shared utilities live in `frontend/lib/utils/`. When the same pattern appears in 2+ places, extract it. When modifying a pattern that exists in a shared helper, modify the helper — not the call sites.

### Mobile Responsive
**All pages must be fully responsive and work on mobile-sized devices.** Design mobile-first, test at 320px-480px viewport widths, use responsive CSS (flexbox, grid, media queries), ensure touch targets are at least 44x44px, and avoid horizontal scrolling.

### Verify Before Complete
**Use Chrome DevTools to confirm a feature works properly before considering it complete.** Test the actual UI in the browser, check console for errors, verify network requests succeed, and validate the user flow end-to-end. Do not rely solely on unit tests or code review.

## Security Requirements
- **All backend API endpoints MUST require authentication** via `get_current_user` unless the business logic explicitly requires public access (e.g., health check, public messaging page).
- **Every new router endpoint** must include `user: dict = Depends(get_current_user)` and verify the requesting user is authorized to access the requested resource.
- **User-scoped data access**: Endpoints that operate on user data (by email, user_id, or client_id) must verify the authenticated user owns or has permission to access that data. Never trust path/query parameters alone.
- **Service-role key usage**: The backend uses the Supabase service_role key (bypasses RLS). This means **authorization enforcement is the backend's responsibility** — do not rely on Supabase RLS as the sole access control mechanism.
- **No sensitive data in URLs**: Avoid passing emails or PII as path parameters where possible; prefer resolving the user from the auth token.

## Build & Run Commands

### Frontend (Next.js)
```bash
cd frontend
npm run dev      # Development server at http://localhost:3000
npm run build    # Production build
npm run lint     # ESLint
```

### Backend (FastAPI)
```bash
cd backend
uv sync                                    # Install dependencies
uv sync --extra test                       # Install with test dependencies
uv run uvicorn app.main:app --reload       # Development server at http://localhost:8000
uv run pytest                              # Run all tests
uv run pytest -k "test_name"               # Run specific test
uv run pytest --cov=app --cov-report=html  # Coverage report
uv run ruff check app/                     # Python linting
```

## Architecture

### System Overview
```
Browser (Next.js Frontend, localhost:3000)
    ↓
Supabase (Auth + PostgreSQL + Storage)
    ↓
FastAPI Backend (localhost:8000)
    ↓
External APIs: Google Cloud Speech/TTS, OpenAI GPT-4o-mini, Resend Email
```

### Backend Structure (Service Layer Pattern)
```
Router (HTTP endpoints) → Service (business logic) → Database Client (Supabase REST)
```

Key directories:
- `backend/app/routers/` - API endpoint definitions (thin: HTTP concerns only)
- `backend/app/services/` - Business logic (all domain logic lives here)
- `backend/app/core/` - Database client, auth, dependencies
- `backend/app/models/` - Pydantic request/response models (per-domain files, re-exported from `schemas.py`)

### Architectural Contracts

#### Service Layer Contract
Routers handle ONLY HTTP concerns: request parsing, status codes, response formatting. ALL business logic lives in services. A router endpoint should be ~5-15 lines: parse request, call service, return response.

#### Service Pattern
Service classes use `__init__(self, db: SupabaseClient)` matching the existing `TreatmentService` pattern. Pure functions (formatters, matchers, generators) live as module-level functions in the same service file.

#### Schema Organization
Models are split into per-domain files under `backend/app/models/` (e.g., `profile.py`, `life_words.py`, `messaging.py`). `backend/app/models/schemas.py` re-exports everything for backward compatibility.

#### Answer Matching
All answer evaluation happens on the backend via `/api/matching/*` endpoints. Frontend sends raw user answers, backend returns match results. No matching logic in frontend code.

#### Frontend API Client
All backend calls go through `frontend/lib/api/client.ts`. No inline `fetch()` calls in pages or components.

#### Shared Service Utilities
Common patterns (ownership checks, session verification, partial updates, soft deletes, entity listing, storage uploads) are centralized in `backend/app/services/utils.py`. Services import and use these helpers instead of reimplementing the same logic. The shared `FRONTEND_URL` constant also lives here.

#### No Raw httpx in Routers
All DB operations use `SupabaseClient`. The client already uses the service role key, so raw httpx is never needed in routers.

#### Testing
75%+ coverage on all new service modules. Function-based tests only, pytest-mock. No test classes.

### Frontend Structure (Next.js App Router)
```
frontend/app/
├── (auth)/           # Public routes: login, signup
├── (dashboard)/      # Protected routes (middleware-guarded)
│   └── treatments/   # Treatment pages: word-finding, life-words, short-term-memory
├── message/          # Public messaging page
└── invite/           # Invite acceptance page
```

Route groups `(auth)` and `(dashboard)` control layout and auth requirements.

### Frontend Rules
1. **Pages are thin**: Compose components + call hooks. No direct fetch() calls, no complex state logic.
2. **Hooks own business logic**: Data fetching, form state, validation, side effects.
3. **Components are presentational**: Accept props, render UI, emit events. No API calls.
4. **Single API client**: All backend calls go through `frontend/lib/api/client.ts`. No raw fetch() in components or hooks.
5. **Contexts are for global state only**: Auth, selected client, voice settings. NOT for page-specific data.

## Database

Uses Supabase PostgreSQL with Row-Level Security (RLS) enabled on all tables. Key tables:
- `profiles` - User profiles (auto-created via trigger from auth.users)
- `treatment_sessions`, `treatment_results`, `user_progress` - Treatment data
- `personal_contacts`, `personal_items` - Life Words user content
- `word_finding_stimuli` - Word finding images and metadata
- `life_words_*` tables - Session and response tracking

### Migration Workflow
When making schema changes, **always create and push the migration in one step**:
1. `cd backend && supabase migration new <descriptive_name>` — creates the SQL file
2. Write the migration SQL (CREATE TABLE, ALTER TABLE, etc.)
3. `cd backend && supabase db push` — applies all pending migrations to the database
4. Never leave migrations unpushed — they should be applied immediately after creation

## Testing

Backend has 526 tests. Use function-based tests only, no test classes.

```python
# Use pytest-mock, not unittest.mock
def test_example(mocker):
    mock_service = mocker.patch("app.services.example_service")
    # ...
```

Integration tests use FastAPI's `dependency_overrides` for mocking auth and database.

## UI/UX Requirements

Target audience is elderly users with cognitive impairments:
- Large fonts (18px base minimum)
- High contrast colors
- Clear, simple navigation
- WCAG AAA compliance goal

## Deployment

GitHub Actions CI/CD triggers on release tags (v*):
1. Runs backend tests (80% minimum coverage required)
2. Builds Docker images → Google Artifact Registry
3. Deploys to Google Cloud Run

Production: words.parrotsoftware.com
