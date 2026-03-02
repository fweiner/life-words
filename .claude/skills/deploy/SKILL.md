---
name: deploy
description: Run tests, fix failures, commit clean code, push migrations to Supabase production, deploy to GCP via GitHub release, and monitor until successful
user-invocable: true
disable-model-invocation: false
---

# Deploy to Production

You are a deployment automation agent. Follow these steps in order. Do not skip steps.

## Step 1: Run All Tests

Tests must pass before anything gets committed or pushed.

### Backend tests
```bash
cd /Users/fredweiner/dev/Life-Words/backend && uv run pytest --cov=app --cov-report=term --cov-fail-under=80 -q
```

### Frontend lint + build
```bash
cd /Users/fredweiner/dev/Life-Words/frontend && npm run lint && npm run build
```

### Frontend unit tests
```bash
cd /Users/fredweiner/dev/Life-Words/frontend && npm test -- --passWithNoTests
```

### Frontend E2E tests
```bash
cd /Users/fredweiner/dev/Life-Words/frontend && npx playwright test
```

If Playwright browsers are not installed, run `npx playwright install chromium --with-deps` first.

If any tests fail:
1. Analyze the failure output
2. Fix the code
3. Re-run the failing test suite
4. Repeat until all tests pass
5. Do NOT proceed to Step 2 until every test suite is green

## Step 2: Check Pending Migrations

Check if there are local migrations not yet applied to the Supabase production database:

```bash
cd /Users/fredweiner/dev/Life-Words && supabase migration list
```

Look for migrations that exist locally but not on remote. If there are pending migrations, they will be pushed in Step 5.

## Step 3: Clean Working Tree

```bash
cd /Users/fredweiner/dev/Life-Words && git status
```

Show the user any uncommitted changes (staged, unstaged, untracked).

If there are changes:
1. Show the user a summary of what changed
2. Stage relevant files (prefer specific file names over `git add .`)
3. Create a descriptive commit message summarizing the changes
4. Commit with the standard format:
   ```
   git commit -m "$(cat <<'EOF'
   <commit message>

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```

If the tree is already clean, proceed.

## Step 4: Determine Version

Get the current version:
```bash
git tag --sort=-v:refname | head -1
```

Ask the user using AskUserQuestion with these options:
- **Breaking change** — increments MAJOR (e.g., 1.2.5 -> 2.0.0). Use when: API contracts change, database schema has breaking changes, existing features removed or fundamentally altered.
- **Feature addition** — increments MINOR (e.g., 1.2.5 -> 1.3.0). Use when: new functionality added, new endpoints, new pages, non-breaking enhancements.
- **Bugfix** — increments PATCH (e.g., 1.2.5 -> 1.2.6). Use when: bug fixes, copy changes, style tweaks, test fixes, dependency updates.

Show the user the current version and what the new version will be. Confirm before proceeding.

Tag the commit:
```bash
git tag v{VERSION}
```

## Step 5: Push Migrations to Supabase Production

If Step 2 found pending migrations, push them now BEFORE deploying code:

```bash
cd /Users/fredweiner/dev/Life-Words && supabase db push
```

If the migration push fails:
1. Read the error carefully
2. Fix the migration SQL if needed
3. Re-run `supabase db push`
4. Do NOT proceed until migrations are applied

If no pending migrations, skip this step.

## Step 6: Push to GitHub

```bash
git push && git push --tags
```

## Step 7: Create GitHub Release

```bash
gh release create v{VERSION} --title "v{VERSION}" --generate-notes
```

This triggers the `deploy-production.yml` GitHub Actions workflow which:
- Runs backend tests (80% coverage gate)
- Runs frontend E2E tests (gates frontend deploy)
- Builds and pushes Docker images to Artifact Registry
- Deploys `treatment-api` and `treatment-web` to Cloud Run

## Step 8: Monitor Deployment

```bash
gh run watch
```

Watch the workflow run to completion. If it fails:

1. Get the failure logs:
   ```bash
   gh run view --log-failed
   ```
2. Analyze the root cause
3. Fix the issue in code
4. Re-run tests locally (Step 1)
5. Commit the fix
6. Increment the PATCH version (e.g., 1.3.0 -> 1.3.1)
7. Tag, push, and create a new release
8. Monitor again
9. Repeat until deployment succeeds

## Step 9: Verify Deployment

Once the workflow succeeds:

1. Report success to the user with:
   - The release version and GitHub release URL
   - Backend status: `gcloud run services describe treatment-api --project=life-words-production --region=us-central1 --format="value(status.url)"`
   - Frontend status: `gcloud run services describe treatment-web --project=life-words-production --region=us-central1 --format="value(status.url)"`
2. Verify the deployed backend is healthy:
   ```bash
   curl -sf https://treatment-api-757821375257.us-central1.run.app/docs > /dev/null && echo "Backend healthy" || echo "Backend unreachable"
   ```

## Rules

- **Tests before commits** — never commit code that hasn't passed all tests
- **Migrations before code deploy** — schema changes must land before the new code that uses them
- **Never force push** to main
- **Never skip hooks** (no `--no-verify`)
- **Always increment version** for every release, even deployment fixes
- **Keep the user informed** at every step
- **Use TaskCreate/TaskUpdate** to track deployment progress
