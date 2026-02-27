# GitHub Secrets Configuration Guide

This guide walks you through setting up GitHub repository secrets for CI/CD deployment of the Life Words application.

## Prerequisites

- Admin access to the GitHub repository: `fweiner/life-words-production`
- Completed setup for:
  - OpenAI API ([01-openai-setup.md](./01-openai-setup.md))
  - Google Cloud Platform ([02-gcp-setup.md](./02-gcp-setup.md))
  - Resend ([03-resend-setup.md](./03-resend-setup.md))
  - Supabase ([06-supabase-setup.md](./06-supabase-setup.md))

## What are GitHub Secrets?

GitHub Secrets are encrypted environment variables that you can use in GitHub Actions workflows. They allow you to store sensitive information like API keys securely without exposing them in your code.

## Step 1: Access Repository Secrets

1. Navigate to your GitHub repository:
   - [https://github.com/fweiner/life-words-production](https://github.com/fweiner/life-words-production)

2. Click on **Settings** (in the repository navigation)

3. In the left sidebar, expand **Secrets and variables**

4. Click **Actions**

You should now see the "Actions secrets and variables" page.

## Step 2: Add Required Secrets

Click **New repository secret** for each of the following secrets:

### 2.1 GCP_PROJECT_ID

- **Name**: `GCP_PROJECT_ID`
- **Value**: `life-words-production`
- Click **Add secret**

**Purpose**: Identifies your Google Cloud Platform project.

### 2.2 GCP_SA_KEY

This is the most complex secret as it requires encoding the GCP service account JSON file.

**On Windows (PowerShell):**
```powershell
# Navigate to where you saved the GCP service account key
cd path\to\your\keys

# Convert to base64
$fileContent = Get-Content -Path "gcp-github-actions.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($fileContent)
$base64 = [Convert]::ToBase64String($bytes)
$base64 | Set-Clipboard
Write-Host "Base64 encoded key copied to clipboard!"
```

**On Windows (Git Bash):**
```bash
cat gcp-github-actions.json | base64 -w 0 | clip
echo "Base64 encoded key copied to clipboard!"
```

**On Mac/Linux:**
```bash
cat gcp-github-actions.json | base64 | pbcopy  # Mac
cat gcp-github-actions.json | base64 -w 0 | xclip  # Linux
echo "Base64 encoded key copied to clipboard!"
```

- **Name**: `GCP_SA_KEY`
- **Value**: Paste the base64-encoded content from your clipboard
- Click **Add secret**

**Purpose**: Authenticates GitHub Actions to deploy to Google Cloud Platform.

### 2.3 SUPABASE_URL

- **Name**: `SUPABASE_URL`
- **Value**: `https://nnvqtxwobvyitqbsdskc.supabase.co`
- Click **Add secret**

**Purpose**: Your Supabase project URL.

**Where to find it**:
1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Select your project
3. Go to **Project Settings** > **API**
4. Copy the **Project URL**

### 2.4 SUPABASE_ANON_KEY

- **Name**: `SUPABASE_ANON_KEY`
- **Value**: Your Supabase publishable/anonymous key
- Click **Add secret**

**Purpose**: Public key for frontend to access Supabase.

**Where to find it**:
1. In Supabase project settings > **API**
2. Copy the **anon** / **public** key under "Project API keys"

### 2.5 SUPABASE_SECRET_KEY

- **Name**: `SUPABASE_SECRET_KEY`
- **Value**: Your Supabase secret/service role key
- Click **Add secret**

**Purpose**: Backend server key for privileged Supabase access.

**Where to find it**:
1. In Supabase project settings > **API**
2. Copy the **service_role** key under "Project API keys"
3. ⚠️ **This is sensitive** - never expose this in frontend code

### 2.6 OPENAI_API_KEY

- **Name**: `OPENAI_API_KEY`
- **Value**: Your OpenAI API key (starts with `sk-proj-`)
- Click **Add secret**

**Purpose**: Enables AI functionality using GPT-4o-mini.

**Where to find it**:
- Use the key you created in [01-openai-setup.md](./01-openai-setup.md)
- If you lost it, create a new one at [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 2.7 RESEND_API_KEY

- **Name**: `RESEND_API_KEY`
- **Value**: Your Resend API key (starts with `re_`)
- Click **Add secret**

**Purpose**: Enables email sending functionality.

**Where to find it**:
- Use the production key you created in [03-resend-setup.md](./03-resend-setup.md)
- Or create a new one at [https://resend.com/api-keys](https://resend.com/api-keys)

### 2.8 GOOGLE_CLOUD_REGION

- **Name**: `GOOGLE_CLOUD_REGION`
- **Value**: `us-central1` (or your preferred region)
- Click **Add secret**

**Purpose**: Specifies which GCP region to deploy to.

**Common regions**:
- `us-central1` - Iowa, USA
- `us-east1` - South Carolina, USA
- `us-west1` - Oregon, USA
- `europe-west1` - Belgium
- `asia-east1` - Taiwan

Choose based on your target users' location.

## Step 3: Verify All Secrets

After adding all secrets, you should see the following in your secrets list:

1. ✅ `GCP_PROJECT_ID`
2. ✅ `GCP_SA_KEY`
3. ✅ `SUPABASE_URL`
4. ✅ `SUPABASE_ANON_KEY`
5. ✅ `SUPABASE_SECRET_KEY`
6. ✅ `OPENAI_API_KEY`
7. ✅ `RESEND_API_KEY`
8. ✅ `GOOGLE_CLOUD_REGION`

**Note**: You won't be able to view the secret values after they're added (only update or delete them).

## Step 4: Test Secrets in Workflow

You can create a simple test workflow to verify secrets are accessible:

**.github/workflows/test-secrets.yml** (temporary test file):

```yaml
name: Test Secrets

on:
  workflow_dispatch:  # Allows manual trigger

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check Secrets
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          OPENAI_KEY_LENGTH: ${{ secrets.OPENAI_API_KEY }}
        run: |
          echo "GCP Project: $GCP_PROJECT_ID"
          echo "Supabase URL: $SUPABASE_URL"
          echo "OpenAI key exists: ${{ secrets.OPENAI_API_KEY != '' }}"
          echo "Resend key exists: ${{ secrets.RESEND_API_KEY != '' }}"
          echo "All secrets loaded successfully!"
```

To run this test:
1. Go to **Actions** tab in your repository
2. Select "Test Secrets" workflow
3. Click "Run workflow"
4. Check the output to verify secrets are loading

**Delete this test file** after verification.

## Step 5: Update Secrets (If Needed)

To update an existing secret:

1. Go to **Settings** > **Secrets and variables** > **Actions**
2. Click on the secret name
3. Click **Update secret**
4. Enter the new value
5. Click **Update secret**

## Security Best Practices

### 1. Secret Rotation

Rotate secrets regularly:
- **API Keys**: Every 90 days
- **Service Account Keys**: Every 90 days
- **Database Keys**: Annually or when team members leave

### 2. Access Control

- Limit who has admin access to the repository
- Review access permissions quarterly
- Use branch protection rules for main branch

### 3. Monitoring

- Enable notifications for failed deployments
- Monitor GCP/OpenAI/Resend usage for anomalies
- Set up budget alerts

### 4. Least Privilege

- Each secret should have minimum required permissions
- Use separate keys for development vs. production
- Don't share secrets across projects

### 5. Audit Trail

- Review GitHub Actions logs regularly
- Monitor secret access patterns
- Enable audit logging in GCP

## Troubleshooting

### Secret Not Found Error

```
Error: Secret SOME_SECRET not found
```

**Solutions**:
1. Verify the secret name matches exactly (case-sensitive)
2. Check the secret exists in **Settings** > **Secrets and variables** > **Actions**
3. Ensure you're referencing it correctly: `${{ secrets.SECRET_NAME }}`

### Base64 Encoding Issues (GCP_SA_KEY)

**Problem**: GitHub Actions fails with authentication errors

**Solutions**:
1. Verify the JSON file is valid (open in text editor)
2. Re-encode without line breaks:
   ```bash
   cat gcp-github-actions.json | base64 -w 0
   ```
3. Ensure no extra characters were copied

### Deployment Fails with Permission Denied

**Problem**: GCP service account lacks permissions

**Solutions**:
1. Verify service account has required roles (see [02-gcp-setup.md](./02-gcp-setup.md))
2. Check that the correct service account key was uploaded
3. Ensure APIs are enabled in GCP

### Secrets Not Updating in Workflow

**Problem**: Updated secret value not reflected in deployment

**Solutions**:
1. Re-run the workflow (secrets are cached)
2. Verify the update was saved
3. Check if you updated the correct repository (not a fork)

## Environment-Specific Secrets (Advanced)

For staging/production separation, you can use **Environments**:

1. Go to **Settings** > **Environments**
2. Click **New environment**
3. Name it `production`
4. Add environment-specific secrets
5. Add protection rules (require approvals, delay deployment, etc.)

In your workflow:
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Uses production environment secrets
```

## Next Steps

After configuring GitHub secrets:
1. Set up domain and deployment: [05-domain-deployment.md](./05-domain-deployment.md)
2. Configure Supabase database: [06-supabase-setup.md](./06-supabase-setup.md)
3. Test the full CI/CD pipeline

## Quick Reference

| Secret Name | Example Value | Where to Get It |
|------------|---------------|-----------------|
| `GCP_PROJECT_ID` | `life-words-production` | GCP Console |
| `GCP_SA_KEY` | `eyJ0eXAi...` (base64) | Encoded JSON file |
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase Settings > API |
| `SUPABASE_ANON_KEY` | `eyJhbGc...` | Supabase Settings > API |
| `SUPABASE_SECRET_KEY` | `eyJhbGc...` | Supabase Settings > API |
| `OPENAI_API_KEY` | `sk-proj-...` | OpenAI Platform |
| `RESEND_API_KEY` | `re_...` | Resend Dashboard |
| `GOOGLE_CLOUD_REGION` | `us-central1` | Your choice |
