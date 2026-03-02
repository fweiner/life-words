---
name: review-standards
description: Review code for DRY violations, thin client/router adherence, test coverage, security, and project standards from CLAUDE.md
user-invocable: true
disable-model-invocation: false
argument-hint: [path-or-scope]
---

# Code Standards Review

Review the specified section of the codebase (or entire codebase if no argument given) against project standards. The scope is: `$ARGUMENTS`

If no scope is provided, ask the user which area to review using AskUserQuestion with options like: "Backend services", "Backend routers", "Frontend pages/components", "Full codebase".

## Review Process

Launch parallel Sonnet agents to review independently, then synthesize findings.

### Agent 1: DRY Violations

Search for duplicated logic across the codebase within the specified scope:

- **Backend**: Look for patterns that should use shared helpers from `backend/app/services/utils.py` (`verify_ownership`, `verify_session`, `build_update_data`, `soft_delete_entity`, `list_user_entities`, `upload_to_storage`, `FRONTEND_URL`). Check if any service reimplements logic that already exists in another service or in utils.
- **Frontend**: Look for duplicated API calls, repeated UI patterns, or logic that should be extracted to `frontend/lib/utils/`. Check for inline `fetch()` calls that should use `apiClient` from `frontend/lib/api/client.ts`.
- Flag any pattern appearing in 2+ places that could be extracted into a shared utility.
- Check for duplicated Pydantic models or response schemas across `backend/app/models/` files.

### Agent 2: Thin Client Architecture

Verify the frontend contains no business logic:

- **No validation logic** in frontend code (beyond basic form UX like "field required"). All real validation must happen on the backend.
- **No data processing or calculations** in pages, components, or hooks. Frontend should only render, interact, and call APIs.
- **No matching/evaluation logic** in frontend. All answer matching goes through `/api/matching/*` endpoints.
- **No inline fetch() calls** in pages or components. All backend calls must go through `apiClient` in `frontend/lib/api/client.ts`. Exception: `textToSpeech.ts` (needs blob response) and local blob URLs (camera preview).
- **Hooks own data fetching logic**, but should not contain domain/business rules.
- **Components are presentational only**: accept props, render UI, emit events. No API calls inside components.

### Agent 3: Thin Routers

Verify backend routers only handle HTTP concerns:

- Each router endpoint should be ~5-15 lines: parse request, call service, return response.
- **No business logic in routers**: no conditionals on data values, no loops over results, no data transformations beyond HTTP response formatting.
- **All domain logic lives in services**: services use `__init__(self, db: SupabaseClient)` pattern.
- **No raw httpx in routers**: all DB operations use `SupabaseClient`.
- Check that routers don't import or use database client directly for complex queries.
- Service instantiation should follow the `TreatmentService` pattern.

### Agent 4: Test Coverage & Quality

Analyze test coverage and quality:

- Run `cd backend && uv run pytest --cov=app --cov-report=term-missing -q 2>&1 | tail -60` to get current coverage.
- Flag any service module below 75% coverage.
- Verify tests are **function-based only** (no test classes).
- Verify tests use **pytest-mock** (not `unittest.mock`).
- Check that integration tests use `dependency_overrides` for mocking auth and database.
- Look for tests that test implementation details rather than behavior.
- Flag any new endpoints without corresponding tests.

### Agent 5: Security & Auth Standards

Verify security requirements:

- **All endpoints require auth**: Every router endpoint must have `user: dict = Depends(get_current_user)` unless explicitly public (health check, public messaging page, matching endpoints).
- **User-scoped data access**: Endpoints operating on user data must verify the authenticated user owns or has permission. Never trust path/query parameters alone.
- **No sensitive data in URLs**: Check for emails or PII passed as path parameters.
- **No secrets in code**: Check for hardcoded API keys, tokens, or credentials.
- **Input validation**: All user input validated via Pydantic models on the backend.
- Check for potential SQL injection, XSS, or command injection vectors.

### Agent 6: Error Handling & Logging

Verify all errors are properly logged to the `error_logs` table and none are swallowed silently:

- **No bare `except` blocks that swallow errors**: Every `except Exception` (or bare `except`) must call `log_error()` from `app.core.error_logger`. Catching an exception and only re-raising as `HTTPException` without logging is a swallowed error.
- **Import check**: Any file with a `try/except` block should import `from app.core.error_logger import log_error` and call it in the except handler.
- **Source tags**: Errors caught and re-raised should use `source="swallowed"`. Errors explicitly logged for monitoring should use `source="manual"`.
- **Context fields**: `log_error()` calls should include relevant context — at minimum `service_name` and `function_name`, plus `endpoint`/`http_method` when available in routers.
- **No `print()` or `logging.error()` as sole error handling**: These do not write to the `error_logs` table and are invisible to admins. They may accompany `log_error()` but must not replace it.
- **Global handler coverage**: Verify `main.py` has a global `@app.exception_handler(Exception)` that calls `log_error(source="unhandled")` as a safety net — but this should not be relied upon as the only error logging. Services and routers that catch exceptions should log them explicitly.
- **No `except Exception as e: pass`**: Silent exception swallowing is never acceptable.

### Agent 7: Migration & Database Standards

Verify database migration practices:

- **No unpushed migrations**: Check for migration files in `backend/supabase/migrations/` that haven't been applied. Run `supabase migration list` if possible.
- **Migration naming**: Migration files should have descriptive names (not just timestamps).
- **No raw SQL in services**: All DB operations go through `SupabaseClient`, never raw SQL queries in service code.
- **Schema alignment**: Pydantic models in `backend/app/models/` should match the database schema defined in migrations.

### Agent 8: Frontend Quality Standards

Review frontend-specific standards:

- **Mobile responsive**: Check for hardcoded pixel widths, missing responsive CSS, or layouts that would break at 320-480px viewports.
- **Accessibility**: Check for missing aria labels, insufficient color contrast patterns, small touch targets (should be 44x44px minimum).
- **Large fonts**: Base font should be 18px minimum for the target elderly audience.
- **Schema organization**: Frontend models/types should align with backend Pydantic schemas.
- **No direct Supabase data queries**: Frontend only uses Supabase for auth (`supabase.auth.getUser()`), never for direct data access.

## Output Format

After all agents complete, synthesize the findings into a structured report:

```
## Code Standards Review: [scope]

### Summary
- X DRY violations found
- X thin client violations found
- X thin router violations found
- X coverage gaps found
- X security concerns found
- X swallowed/unlogged errors found
- X migration/database issues found
- X frontend quality issues found

### Critical Issues (fix immediately)
[Issues that violate security requirements or core architecture]

### Standards Violations (should fix)
[DRY violations, thin client/router violations, coverage gaps]

### Recommendations (nice to have)
[Suggestions for improvement that aren't strict violations]

### Passing Checks
[Areas that are in good shape - brief acknowledgment]
```

For each issue found, include:
1. **File path and line number**
2. **What the violation is**
3. **Which standard it violates** (reference CLAUDE.md section)
4. **Suggested fix** (brief, actionable)

## Important Notes

- Do NOT make any code changes. This is a read-only review.
- Do NOT run the full test suite if it would take more than 2 minutes. Use `--cov-report=term-missing -q` for quick coverage checks.
- Focus on real, actionable issues. Avoid nitpicks that a linter would catch.
- Reference specific CLAUDE.md sections when flagging violations.
- If the scope is a single file or directory, focus the review there but note any cross-cutting concerns.
