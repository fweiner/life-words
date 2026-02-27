# Google Cloud Platform Setup Guide

This guide walks you through setting up Google Cloud Platform (GCP) for the Life Words application, including Speech-to-Text, Text-to-Speech, Cloud Run, and service accounts.

## Prerequisites

- A Google account
- A credit card for billing (GCP requires payment information, but offers free tier)

## Step 1: Create/Access GCP Project

### 1.1 Navigate to Google Cloud Console

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Sign in with your Google account
3. Accept the Terms of Service if prompted

### 1.2 Create the Project

1. Click the project dropdown at the top of the page
2. Click **NEW PROJECT**
3. Project details:
   - **Project name**: `Life Words`
   - **Project ID**: `life-words-production` (must be globally unique)
   - **Organization**: Select if applicable (or leave as "No organization")
4. Click **CREATE**
5. Wait for the project to be created (usually takes a few seconds)
6. Select the project from the dropdown

## Step 2: Enable Billing

1. In the left sidebar, go to **Billing**
2. Click **LINK A BILLING ACCOUNT**
3. Either:
   - Select an existing billing account, OR
   - Click **CREATE BILLING ACCOUNT** and enter payment details
4. Complete the billing setup

**Note**: GCP offers a free tier and $300 credit for new users.

## Step 3: Enable Required APIs

You need to enable the following APIs:

1. Go to **APIs & Services** > **Enable APIs and Services**
2. Search for and enable each of the following:

### Required APIs:

1. **Cloud Run API**
   - Search: "Cloud Run API"
   - Click the result
   - Click **ENABLE**

2. **Artifact Registry API**
   - Search: "Artifact Registry API"
   - Click **ENABLE**

3. **Cloud Speech-to-Text API**
   - Search: "Cloud Speech-to-Text API"
   - Click **ENABLE**

4. **Cloud Text-to-Speech API**
   - Search: "Cloud Text-to-Speech API"
   - Click **ENABLE**

5. **Cloud Build API** (for CI/CD)
   - Search: "Cloud Build API"
   - Click **ENABLE**

## Step 4: Create Service Accounts

You'll need two service accounts:
1. **CI/CD Service Account** - For GitHub Actions to deploy
2. **Runtime Service Account** - For the application to use Speech APIs locally

### 4.1 Create CI/CD Service Account

1. Go to **IAM & Admin** > **Service Accounts**
2. Click **+ CREATE SERVICE ACCOUNT**
3. Service account details:
   - **Name**: `github-actions-deploy`
   - **Description**: `Service account for GitHub Actions CI/CD pipeline`
4. Click **CREATE AND CONTINUE**

5. Grant roles (click **+ ADD ANOTHER ROLE** for each):
   - **Cloud Run Admin** (`roles/run.admin`)
   - **Service Account User** (`roles/iam.serviceAccountUser`)
   - **Artifact Registry Writer** (`roles/artifactregistry.writer`)
   - **Storage Admin** (`roles/storage.admin`)
6. Click **CONTINUE**
7. Click **DONE**

### 4.2 Create Runtime Service Account

1. Click **+ CREATE SERVICE ACCOUNT** again
2. Service account details:
   - **Name**: `treatment-app-runtime`
   - **Description**: `Runtime service account for Speech APIs`
3. Click **CREATE AND CONTINUE**

4. Grant roles:
   - **Cloud Speech-to-Text User** (`roles/speech.client`)
   - **Cloud Text-to-Speech User** (`roles/texttospeech.client`)
5. Click **CONTINUE**
6. Click **DONE**

## Step 5: Create and Download Service Account Keys

### 5.1 Download CI/CD Key

1. In the Service Accounts list, find **github-actions-deploy**
2. Click the three dots (⋮) on the right
3. Select **Manage keys**
4. Click **ADD KEY** > **Create new key**
5. Select **JSON** format
6. Click **CREATE**
7. Save the downloaded file as `gcp-github-actions.json`
8. **Store this file securely** - it will be used for GitHub secrets

### 5.2 Download Runtime Key

1. In the Service Accounts list, find **treatment-app-runtime**
2. Click the three dots (⋮) on the right
3. Select **Manage keys**
4. Click **ADD KEY** > **Create new key**
5. Select **JSON** format
6. Click **CREATE**
7. Save the downloaded file as `gcp-runtime.json`
8. Move this file to your project backend directory (for local development)

## Step 6: Set Up Artifact Registry

1. Go to **Artifact Registry** in the left sidebar
2. Click **+ CREATE REPOSITORY**
3. Repository details:
   - **Name**: `treatment-app`
   - **Format**: **Docker**
   - **Mode**: **Standard**
   - **Location type**: **Region**
   - **Region**: **us-central1** (or your preferred region)
4. Click **CREATE**

## Step 7: Configure Local Development

### 7.1 Add Runtime Key to Backend

1. Copy the runtime service account key to your backend directory:
   ```bash
   cp path/to/gcp-runtime.json backend/gcp-runtime.json
   ```

2. Update `backend/.env`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=gcp-runtime.json
   GOOGLE_CLOUD_PROJECT=life-words-production
   ```

3. Verify `.gitignore` includes:
   ```
   gcp-*.json
   *-service-account.json
   ```

## Step 8: Test Speech APIs

### 8.1 Test Speech-to-Text

You can test the Speech API using the Google Cloud Console:

1. Go to **Speech-to-Text** in the console
2. Try the demo with your microphone
3. Verify it works

### 8.2 Test Text-to-Speech

1. Go to **Text-to-Speech** in the console
2. Enter sample text
3. Click **Speak it**
4. Verify audio plays

## Step 9: Set Up Budget Alerts (Recommended)

1. Go to **Billing** > **Budgets & alerts**
2. Click **CREATE BUDGET**
3. Budget details:
   - **Name**: `Treatment App Monthly Budget`
   - **Projects**: Select `life-words-production`
   - **Services**: All services
   - **Time range**: Monthly
4. Set budget amount (e.g., $50/month)
5. Set alert thresholds:
   - 50% of budget
   - 90% of budget
   - 100% of budget
6. Add email recipients
7. Click **FINISH**

## Cost Estimates

### Cloud Run (Serverless)
- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests
- **Free tier**: 2 million requests/month

**Estimated monthly cost with minimal traffic**: $0-5

### Speech-to-Text
- **Standard model**: $0.006 per 15 seconds
- For 1-30 second clips: ~$0.006-0.012 per request
- **Free tier**: 60 minutes/month

**Estimated cost for 1000 sessions/month**: ~$6-12

### Text-to-Speech
- **Standard voices**: $4.00 per 1M characters
- **WaveNet voices**: $16.00 per 1M characters
- For 100-500 character responses: ~$0.0004-0.008 per request

**Estimated cost for 1000 sessions/month**: ~$0.40-8.00

**Total estimated monthly cost (low traffic)**: $6-25

## Security Best Practices

1. **Never commit service account keys to Git**
   - Already excluded in `.gitignore`
   - Double-check before committing

2. **Use separate service accounts for different purposes**
   - CI/CD vs. Runtime
   - Different permissions = better security

3. **Rotate service account keys periodically**
   - Create new keys every 90 days
   - Delete old keys

4. **Monitor API usage**
   - Check the GCP console weekly
   - Set up budget alerts

5. **Use the principle of least privilege**
   - Only grant necessary permissions
   - Review IAM roles quarterly

## Troubleshooting

### "Permission Denied" Errors

- Verify the correct service account is being used
- Check that all required APIs are enabled
- Ensure IAM roles are correctly assigned

### "Quota Exceeded" Errors

- Check your quota limits in **IAM & Admin** > **Quotas**
- Request quota increases if needed
- Monitor usage in the console

### Service Account Key Not Working

- Verify the JSON file is not corrupted
- Check the `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to the correct file
- Ensure the service account has the necessary permissions

## Next Steps

After setting up GCP:
1. Configure Resend for emails: [03-resend-setup.md](./03-resend-setup.md)
2. Set up GitHub secrets: [04-github-secrets.md](./04-github-secrets.md)
3. Deploy to Cloud Run: [05-domain-deployment.md](./05-domain-deployment.md)
