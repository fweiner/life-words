---
name: e2e-test
description: Comprehensive end-to-end testing. Launches parallel sub-agents to research the codebase (structure, database schema, potential bugs), then uses Chrome DevTools MCP tools to test every user journey — taking screenshots, validating UI/UX/accessibility, and querying the database to verify records. Generates Playwright test files for regression testing.
user-invocable: true
disable-model-invocation: false
argument-hint: [journey-scope]
---

# End-to-End Application Testing

Test scope: `$ARGUMENTS`

If no scope is provided, test all user journeys. If a scope is given (e.g., "messaging", "life-words", "auth", "admin"), focus testing on that area.

## Pre-flight Checks

### 1. Verify Servers Are Running

Check that both the backend and frontend dev servers are accessible:

```bash
curl -sf http://localhost:8000/docs > /dev/null && echo "Backend OK" || echo "Backend NOT running"
curl -sf http://localhost:3000 > /dev/null && echo "Frontend OK" || echo "Frontend NOT running"
```

If either server is not running, inform the user:

> "The dev servers need to be running for E2E testing. Start them with:"
> - Backend: `cd backend && uv run uvicorn app.main:app --reload`
> - Frontend: `cd frontend && npm run dev`

**Do NOT start the servers yourself.** Wait for the user to start them and confirm.

### 2. Verify Chrome DevTools MCP

Confirm Chrome DevTools MCP tools are available by listing browser pages:

```
mcp__chrome-devtools__list_pages
```

If this fails, inform the user they need Chrome open with DevTools MCP connected.

### 3. Check Database Access

Verify Supabase CLI is available and can reach the database:

```bash
cd backend && supabase db execute "SELECT count(*) FROM profiles" 2>/dev/null
```

If Supabase CLI is not linked, fall back to the backend API for data verification:

```bash
# Test backend API health
curl -sf http://localhost:8000/docs > /dev/null && echo "Will use backend API for data verification"
```

Note which method is available for Phase 4 database validation.

## Phase 1: Parallel Research

Launch **three sub-agents simultaneously** using the Agent tool. All three run in parallel.

### Sub-agent 1: Application Structure & User Journeys

> Research this codebase thoroughly. Return a structured summary covering:
>
> 1. **Every user-facing route/page** — read `frontend/app/` recursively to find all `page.tsx` files. For each, note the URL path, whether it requires auth (under `(dashboard)/` route group), and what it renders.
> 2. **Every user journey** — complete flows a user can take. Key journeys include:
>    - **Auth flow**: Sign up, login, password reset, logout
>    - **Onboarding**: First-time user setup, adding contacts, adding items
>    - **Life Words practice**: Creating sessions, answering questions, viewing results
>    - **Information practice**: Entering personal information, practicing recall
>    - **Question practice**: Answering life-words questions
>    - **Contact management**: Add, edit, delete contacts (including quick-add with photo)
>    - **Item management**: Add, edit, delete personal items
>    - **Messaging**: View conversations, send messages, public messaging
>    - **Settings**: Profile editing, match accommodation settings, voice settings
>    - **Admin**: User management, error log review
>    - **Subscription**: Stripe checkout, subscription management
>    - **Invite flow**: Sending invites, accepting invites with token
>    - **Progress**: Viewing practice progress and results
>    - **Preparation**: Step-by-step preparation page
> 3. **For each journey**: List specific steps, form fields, interactive elements, and expected outcomes
> 4. **Key UI components**: Forms, modals, dropdowns, camera inputs, speech recognition buttons, and other interactive elements
> 5. **Protected vs public routes**: Which routes are behind auth middleware and which are public
>
> Read the actual page.tsx files to understand what each page renders and what API calls it makes. Be exhaustive.

### Sub-agent 2: Database Schema & Data Flows

> Research the database layer of this codebase. Return a structured summary:
>
> 1. **Database setup**: Supabase PostgreSQL. Read `backend/app/core/database.py` to understand the client setup.
> 2. **Full schema**: Read ALL migration files in `backend/supabase/migrations/` to map every table, column, type, constraint, and relationship. Also check `backend/app/models/` for Pydantic schemas that mirror the database tables.
> 3. **Key tables and their purposes**:
>    - `profiles` — user profiles with subscription and match accommodation fields
>    - `personal_contacts` — contacts for life-words practice
>    - `personal_items` — items for life-words practice
>    - `treatment_sessions`, `treatment_results`, `user_progress` — treatment tracking
>    - `life_words_*` tables — session and response tracking
>    - `word_finding_stimuli` — word finding images
>    - Any messaging, invite, or admin tables
> 4. **Data flows per user action**: For each user-facing action (form submit, button click, practice answer), document which tables get created/updated/deleted
> 5. **Validation queries**: For each data flow, provide the exact SQL query to verify records after the action. Format as:
>    ```sql
>    -- After: [user action description]
>    SELECT ... FROM ... WHERE ...;
>    ```
> 6. **Data integrity checks**: Queries to find orphaned records, missing relationships, or inconsistent state:
>    ```sql
>    -- Orphaned contacts (no matching profile)
>    SELECT * FROM personal_contacts WHERE user_id NOT IN (SELECT id FROM profiles);
>    ```

### Sub-agent 3: Bug Hunting

> Analyze this codebase for potential bugs, issues, and code quality problems. Focus on:
>
> 1. **Logic errors** — incorrect conditionals, off-by-one errors, missing null checks, race conditions in async code
> 2. **UI/UX issues** — missing error handling in forms, no loading states, broken responsive layouts, accessibility problems (especially important: this app targets elderly users with cognitive impairments, must meet WCAG AAA)
> 3. **Data integrity risks** — missing validation, potential orphaned records, incorrect cascade behavior, missing foreign key checks in services
> 4. **Security concerns** — endpoints missing `get_current_user`, missing ownership verification, unvalidated input, exposed PII in URLs
> 5. **Frontend thin-client violations** — any business logic in the frontend that should be on the backend
> 6. **API client violations** — any direct `fetch()` calls that should use `apiClient` from `frontend/lib/api/client.ts`
> 7. **Mobile responsiveness** — layouts that might break at 320-480px widths, touch targets smaller than 44x44px
> 8. **Accessibility** — missing ARIA labels, insufficient contrast, keyboard navigation issues, screen reader problems
>
> Return a prioritized list with file paths and line numbers. Categorize as: Critical, High, Medium, Low.

**Wait for all three sub-agents to complete before proceeding.**

## Phase 2: Database Exploration

Using Sub-agent 2's schema findings, query the database to understand current data state:

### If Supabase CLI is available:

```bash
cd backend

# Table row counts
supabase db execute "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"

# Profile count and sample
supabase db execute "SELECT count(*) FROM profiles"
supabase db execute "SELECT id, email, role, first_name, subscription_plan FROM profiles LIMIT 5"

# Content counts
supabase db execute "SELECT count(*) as contact_count FROM personal_contacts"
supabase db execute "SELECT count(*) as item_count FROM personal_items"
supabase db execute "SELECT count(*) as session_count FROM treatment_sessions"

# Data integrity checks from Sub-agent 2
# Run each integrity query identified
```

### If using backend API fallback:

Use authenticated API calls. You will need a valid auth token — check if there is a test user or ask the user to provide one:

```bash
# Example: Get profile via API
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/profile
```

Document all findings about the current database state for use during testing.

## Phase 3: Create Task List

Using the user journeys from Sub-agent 1 and bug findings from Sub-agent 3, create a task (using TaskCreate) for each testable journey. Each task should include:

- **subject:** The journey name (e.g., "Test contact management flow")
- **description:** Steps to execute, expected outcomes, database records to verify, and any related bug findings from Sub-agent 3
- **activeForm:** Present continuous (e.g., "Testing contact management flow")

Filter tasks based on `$ARGUMENTS` scope if provided. Always include these core tasks:

1. One task per identified user journey
2. A task for "Accessibility and responsive testing"
3. A task for "Generate Playwright test files"
4. A final task for "Compile E2E test report"

## Phase 4: User Journey Testing

For each task, mark it `in_progress` with TaskUpdate and execute the following.

### 4a. Browser Testing with Chrome DevTools MCP

Use Chrome DevTools MCP tools for all browser interaction. The key tools are:

| Action | Tool |
|--------|------|
| Navigate to URL | `mcp__chrome-devtools__navigate_page` with `type: "url"` and `url: "..."` |
| Get page elements | `mcp__chrome-devtools__take_snapshot` |
| Click element | `mcp__chrome-devtools__click` with `uid: "..."` |
| Fill input field | `mcp__chrome-devtools__fill` with `uid: "..."` and `value: "..."` |
| Fill multiple fields | `mcp__chrome-devtools__fill_form` with `elements: [...]` |
| Take screenshot | `mcp__chrome-devtools__take_screenshot` (optionally with `filePath`) |
| Press key | `mcp__chrome-devtools__press_key` with `key: "Enter"` |
| Check console errors | `mcp__chrome-devtools__list_console_messages` with `types: ["error", "warn"]` |
| Set viewport size | `mcp__chrome-devtools__resize_page` with `width` and `height` |
| Wait for text | `mcp__chrome-devtools__wait_for` with `text: ["..."]` |
| Hover element | `mcp__chrome-devtools__hover` with `uid: "..."` |
| Check network | `mcp__chrome-devtools__list_network_requests` |
| Run JS | `mcp__chrome-devtools__evaluate_script` with `function: "() => { ... }"` |

**UIDs become invalid after navigation or DOM changes.** Always take a new snapshot after page navigation, form submissions, or dynamic content updates (modals, tabs, dialogs).

For each step in a user journey:

1. Take a snapshot to get current element UIDs
2. Perform the interaction (click, fill, navigate)
3. Wait for the page to settle (use `wait_for` with expected text)
4. **Take a screenshot** — save to `e2e-screenshots/` organized by journey:
   - `e2e-screenshots/auth/01-login-page.png`
   - `e2e-screenshots/contacts/03-form-submitted.png`
   - `e2e-screenshots/responsive/mobile-dashboard.png`
5. **Analyze the screenshot** — use the Read tool to view the screenshot. Check for:
   - Visual correctness and proper rendering
   - Font sizes (18px minimum for this elderly user audience)
   - Touch target sizes (44x44px minimum)
   - Color contrast (WCAG AAA goal)
   - Layout integrity (no overflow, no horizontal scroll)
   - Error states and loading indicators
6. **Check console** — use `list_console_messages` with `types: ["error", "warn"]` to catch JS issues
7. **Check network** — use `list_network_requests` to verify API calls succeed (no 4xx/5xx)

Be thorough. Exercise EVERY interactive element, EVERY form field, EVERY button.

### 4b. Database Validation

After any interaction that should modify data (form submits, deletions, updates), verify the database:

**With Supabase CLI:**
```bash
cd backend && supabase db execute "SELECT * FROM [table] WHERE [condition] ORDER BY created_at DESC LIMIT 5"
```

**With backend API:**
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/[endpoint]
```

Verify:
- Records created/updated/deleted as expected
- Values match what was entered in the UI
- Relationships between records are correct (e.g., contact belongs to the right user)
- No orphaned or duplicate records
- Timestamps are reasonable
- Soft deletes use `deleted_at` (not hard deletes)

### 4c. Issue Handling

When an issue is found (UI bug, database mismatch, JS error, accessibility violation):

1. **Document it:** Expected vs actual behavior, screenshot path, relevant DB query results, severity (Critical/High/Medium/Low)
2. **Fix the code** — make the correction directly in the source files
3. **Re-test the failing step** to verify the fix worked
4. **Take a new screenshot** confirming the fix
5. **Note the fix** for the final report

### 4d. Accessibility & Responsive Testing

For the accessibility/responsive task, test key pages at these viewports:

```
Mobile:  375 x 812   (iPhone-sized)
Tablet:  768 x 1024  (iPad-sized)
Desktop: 1440 x 900  (Standard desktop)
```

At each viewport, for each major page:

1. Resize: `mcp__chrome-devtools__resize_page` with width and height
2. Screenshot the page
3. Check for:
   - **No horizontal scroll**: `mcp__chrome-devtools__evaluate_script` with `() => ({ scrollWidth: document.body.scrollWidth, innerWidth: window.innerWidth, overflows: document.body.scrollWidth > window.innerWidth })`
   - **Font sizes**: `() => { const els = document.querySelectorAll('p, span, label, button, a, h1, h2, h3, td, th, li'); const small = []; els.forEach(el => { const size = parseFloat(getComputedStyle(el).fontSize); if (size < 18 && el.textContent.trim()) small.push({ text: el.textContent.trim().slice(0, 40), size, tag: el.tagName }); }); return small.slice(0, 20); }`
   - **Touch targets**: `() => { const els = document.querySelectorAll('button, a, input, select, [role="button"]'); const small = []; els.forEach(el => { const rect = el.getBoundingClientRect(); if ((rect.width < 44 || rect.height < 44) && rect.width > 0) small.push({ text: el.textContent?.trim().slice(0, 30), width: rect.width, height: rect.height, tag: el.tagName }); }); return small.slice(0, 20); }`
   - **Color contrast**: Check visually from screenshots for low-contrast text
   - **Layout integrity**: No overlapping elements, no cut-off text, proper spacing

After completing each journey task, mark it as `completed` with TaskUpdate.

## Phase 5: Generate Playwright Test Files

After interactive testing is complete, generate Playwright test files based on the journeys tested. Create test files that use the existing test infrastructure.

### Test file template:

```typescript
import { test, expect } from '@playwright/test'
import { mockAuthAndApis, mockAuth } from './fixtures/test-helpers'

test.describe('[Journey Name]', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuthAndApis(page)
  })

  test('[specific test case]', async ({ page }) => {
    await page.goto('/[path]')
    // ... assertions based on what was validated during interactive testing
  })
})
```

### Guidelines for generated tests:

1. **Use existing fixtures**: Import from `frontend/e2e/fixtures/test-helpers.ts`
2. **Mock API responses**: Use `page.route()` to mock backend API responses with realistic data based on database schema findings
3. **Follow Playwright route priority**: Register catch-all `**/api/**` FIRST, then specific routes
4. **Test both desktop and mobile**: Include viewport-specific tests using `test.use({ viewport: { width: 375, height: 812 } })`
5. **No horizontal scroll checks**: Include `expect(document.body.scrollWidth).toBeLessThanOrEqual(window.innerWidth)` for mobile tests
6. **Test loading states**: Verify loading indicators appear before data loads
7. **Test error states**: Mock API errors to verify error handling UI
8. **Test navigation**: Verify links and buttons navigate to correct pages
9. **Test forms**: Fill and submit forms, verify success/error feedback
10. **File naming**: `frontend/e2e/[journey-name].spec.ts`

Write each test file using the Write tool. Base test assertions on actual findings from Phase 4 — only assert things you verified work correctly (or should work after fixes).

## Phase 6: Cleanup

After all testing is complete:

1. Ensure the browser is in a clean state
2. Verify all generated test files are syntactically valid:
   ```bash
   cd frontend && npx tsc --noEmit e2e/*.spec.ts 2>&1 | head -30
   ```
3. Optionally run the generated Playwright tests:
   ```bash
   cd frontend && npx playwright test --project=chromium 2>&1 | tail -40
   ```

## Phase 7: Report

### Text Summary (always output)

Present a concise summary:

```
## E2E Testing Complete

**Journeys Tested:** [count]
**Screenshots Captured:** [count]
**Issues Found:** [count] ([count] fixed, [count] remaining)
**Playwright Tests Generated:** [count] files, [count] test cases

### Issues Fixed During Testing
- [Description] — [file:line] — [severity]

### Remaining Issues
- [Description] — [severity] — [file:line]

### Bug Hunt Findings (from code analysis)
- [Description] — [severity] — [file:line]

### Database Integrity
- [Summary of data integrity check results]
- [Any orphaned records, inconsistencies, or concerns]

### Accessibility Report
- Font size violations: [count] elements below 18px minimum
- Touch target violations: [count] elements below 44x44px minimum
- Responsive issues: [list any viewport problems]

### Generated Test Files
- [file path] — [count] test cases — [what it covers]

### Screenshots
All saved to: `e2e-screenshots/`
```

### Markdown Export (ask first)

After the text summary, ask the user:

> "Would you like me to export the full testing report to `e2e-test-report.md`? It includes per-journey breakdowns, all screenshot references, database validation results, and detailed findings."

If yes, write a detailed report to `e2e-test-report.md` in the project root.

## Important Notes

- **CLAUDE.md compliance**: All fixes must follow the project's architectural standards (thin client, DRY, service layer pattern, security requirements)
- **No secrets in code**: Never hardcode API keys or credentials. Use environment variables.
- **Auth-protected endpoints**: Remember that all backend endpoints require auth via `get_current_user` unless explicitly public.
- **Service role key**: The backend uses Supabase service_role key (bypasses RLS), so authorization is the backend's responsibility.
- **Elderly users**: This app targets people with cognitive impairments. Accessibility is not optional — 18px minimum fonts, 44px minimum touch targets, high contrast, simple navigation.
- **Screenshot organization**: Keep screenshots organized by journey in `e2e-screenshots/` subdirectories.
- **Don't break existing tests**: Generated Playwright tests should coexist with the existing `life-words-home.spec.ts` without conflicts.
