# Secret Manager Migration Guide

This guide explains how to migrate from GitHub Secrets to GCP Secret Manager for improved security and management.

## Why Use Secret Manager?

- **Better Security**: Secrets are stored in GCP with fine-grained access control
- **Centralized Management**: All secrets in one place, easier to rotate
- **Audit Logging**: Track who accessed which secrets and when
- **Version Control**: Keep multiple versions of secrets
- **No Exposure**: Secrets never leave GCP infrastructure during deployment

## Prerequisites

1. Authenticated with gcloud: `gcloud auth login`
2. Correct project set: `gcloud config set project life-words-production`
3. GitHub secrets currently configured (we'll migrate these)

## Step 1: Create Secrets in GCP Secret Manager

Run the setup script to create all required secrets:

```bash
cd scripts
chmod +x create-gcp-secrets.sh
./create-gcp-secrets.sh
```

You'll be prompted to enter:
- `SUPABASE_SECRET_KEY` - Your Supabase service role key
- `SUPABASE_ANON_KEY` - Your Supabase public anon key
- `OPENAI_API_KEY` - Your OpenAI API key
- `RESEND_API_KEY` - Your Resend email API key (optional)

The script will:
1. Create secrets in GCP Secret Manager
2. Grant access to the Cloud Run service account
3. List all created secrets

## Step 2: Verify Secrets

Check that all secrets were created:

```bash
gcloud secrets list --project=life-words-production
```

You should see:
- `production-supabase-url`
- `production-supabase-secret-key`
- `production-supabase-anon-key`
- `openai-api-key`
- `resend-api-key`

## Step 3: Test the Deployment

The updated workflow is already in `.github/workflows/deploy-production.yml` and uses Secret Manager.

Create a test release to verify:

```bash
git tag v0.2.0
git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0 - Secret Manager Migration" --notes "Migrated to GCP Secret Manager"
```

Watch the deployment:

```bash
gh run watch --exit-status
```

## How It Works

### Backend Deployment

The backend now uses `--set-secrets` instead of `--set-env-vars`:

```yaml
--set-secrets="SUPABASE_URL=production-supabase-url:latest,SUPABASE_SECRET_KEY=production-supabase-secret-key:latest,..."
```

Cloud Run automatically:
1. Fetches secrets from Secret Manager at runtime
2. Injects them as environment variables
3. Never exposes them in logs or configuration

### Frontend Deployment

The frontend fetches secrets during the build step:

```yaml
- name: Fetch build secrets from Secret Manager
  run: |
    SUPABASE_URL=$(gcloud secrets versions access latest --secret="production-supabase-url")
    echo "::add-mask::$SUPABASE_URL"  # Masks in logs
    echo "supabase_url=$SUPABASE_URL" >> $GITHUB_OUTPUT
```

Then uses them as build arguments (they're baked into the Next.js bundle).

## Secret Naming Convention

- **Environment-prefixed**: `production-*` for prod, `development-*` for dev
- **Shared secrets**: `openai-api-key`, `resend-api-key` (used across environments)
- **Latest version**: Always use `:latest` to get the current version

## Managing Secrets

### View a Secret's Metadata

```bash
gcloud secrets describe production-supabase-url --project=life-words-production
```

### Update a Secret

```bash
echo -n "new-secret-value" | gcloud secrets versions add production-supabase-url --data-file=-
```

### View Secret Versions

```bash
gcloud secrets versions list production-supabase-url --project=life-words-production
```

### Access a Secret (requires permissions)

```bash
gcloud secrets versions access latest --secret="production-supabase-url"
```

## Security Best Practices

1. **Least Privilege**: Only grant `secretmanager.secretAccessor` to services that need it
2. **Rotation**: Rotate secrets regularly using version management
3. **Monitoring**: Enable audit logs to track secret access
4. **Separation**: Use environment prefixes (production-*, development-*)
5. **Never Log**: Use `::add-mask::` in workflows to prevent logging secrets

## Troubleshooting

### "Permission denied" errors

Grant the Cloud Run service account access:

```bash
PROJECT_NUMBER=$(gcloud projects describe life-words-production --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding production-supabase-url \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

### "Secret not found" errors

Verify the secret exists and the name is correct:

```bash
gcloud secrets list --project=life-words-production
```

### Workflow fails to fetch secrets

Ensure the GitHub Actions service account has Secret Manager access:

```bash
gcloud projects add-iam-policy-binding life-words-production \
  --member="serviceAccount:github-actions-deploy@life-words-production.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Rollback

If you need to rollback to GitHub Secrets:

1. Revert the workflow file changes
2. Keep the GCP secrets (they won't interfere)
3. Redeploy using a new release

The old workflow configuration is available in git history:

```bash
git show v0.1.3:.github/workflows/deploy-production.yml
```

## Next Steps

After successful migration:

1. Consider setting up development environment secrets
2. Enable Secret Manager audit logging
3. Set up secret rotation schedules
4. Document secret rotation procedures
