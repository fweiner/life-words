# Domain Deployment Guide

This guide walks you through deploying the Life Words application to Google Cloud Run and configuring the custom domain `words.parrotsoftware.com`.

## Prerequisites

- Completed all previous setup guides
- GitHub repository with code pushed to `main` branch
- All GitHub secrets configured ([04-github-secrets.md](./04-github-secrets.md))
- Access to GoDaddy DNS for `parrotsoftware.com`

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         words.parrotsoftware.com          │
│      (Next.js Frontend - Cloud Run)     │
└──────────────┬──────────────────────────┘
               │
               ├─── Supabase (Auth, DB, Storage)
               │
               ▼
┌─────────────────────────────────────────┐
│         api.parrotsoftware.com          │
│      (FastAPI Backend - Cloud Run)      │
└─────────────────────────────────────────┘
               │
               ├─── Google Cloud Speech APIs
               └─── OpenAI API
```

## Step 1: Initial Deployment via GitHub Actions

### 1.1 Verify GitHub Actions Workflow

Ensure the workflow file exists at `.github/workflows/deploy-production.yml` (this will be created in a later step).

### 1.2 Create a GitHub Release

The deployment is triggered by creating a release with a version tag:

1. Go to your GitHub repository:
   - [https://github.com/fweiner/life-words-production](https://github.com/fweiner/life-words-production)

2. Click on **Releases** (in the right sidebar)

3. Click **Create a new release** (or **Draft a new release**)

4. Fill in release details:
   - **Choose a tag**: `v1.0.0` (click "Create new tag on publish")
   - **Release title**: `v1.0.0 - Initial Release`
   - **Description**:
     ```markdown
     ## Initial Release

     ### Features
     - Authentication system (username/password)
     - Word Finding treatment app
     - Life Words treatment app
     - Progress tracking dashboard
     - Accessibility features for 65+ users

     ### Infrastructure
     - Next.js frontend on Cloud Run
     - FastAPI backend on Cloud Run
     - Supabase database and storage
     - Google Cloud Speech APIs
     ```
   - **Set as the latest release**: ✅ (checked)

5. Click **Publish release**

### 1.3 Monitor Deployment

1. Go to the **Actions** tab in your repository

2. You should see a workflow run starting:
   - Name: "Deploy to Production"
   - Triggered by: Release v1.0.0

3. Click on the workflow run to view progress

4. Monitor the two jobs:
   - ✅ **Deploy Backend** (~5-10 minutes)
   - ✅ **Deploy Frontend** (~5-10 minutes)

**Common Issues**:
- If deployment fails, check the logs in GitHub Actions
- Verify all secrets are configured correctly
- Ensure GCP APIs are enabled

### 1.4 Verify Initial Deployment

After successful deployment, you can access the services via their default Cloud Run URLs:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Run**
3. Find your services:
   - `treatment-api`
   - `treatment-web`
4. Click each service and note the URL (e.g., `https://treatment-api-xxx-uc.a.run.app`)
5. Test the backend: Open `https://treatment-api-xxx-uc.a.run.app/health` in browser
6. Test the frontend: Open the frontend URL

## Step 2: Configure Custom Domain in Cloud Run

### 2.1 Map Backend Domain (api.parrotsoftware.com)

1. In Google Cloud Console, go to **Cloud Run**

2. Click **Manage Custom Domains** (at the top)

3. Click **Add Mapping**

4. Configure mapping:
   - **Service**: Select `treatment-api`
   - **Region**: `us-central1` (or your chosen region)
   - **Domain**: Select "Verify a new domain" if this is your first time

5. **Domain Verification**:
   - If prompted, verify ownership of `parrotsoftware.com`:
     - Add the provided TXT record to GoDaddy DNS
     - Record Type: `TXT`
     - Host: `@` or as specified
     - Value: `google-site-verification=xxx...`
     - Wait for verification (can take a few minutes)

6. After domain verification, continue mapping:
   - **Subdomain**: Enter `api.parrotsoftware.com`
   - Click **Continue**

7. Cloud Run will provide DNS records (write these down):
   ```
   Type: A
   Name: api
   Value: 216.239.32.21

   Type: A
   Name: api
   Value: 216.239.34.21

   Type: A
   Name: api
   Value: 216.239.36.21

   Type: A
   Name: api
   Value: 216.239.38.21

   Type: AAAA
   Name: api
   Value: 2001:4860:4802:32::15

   Type: AAAA
   Name: api
   Value: 2001:4860:4802:34::15

   Type: AAAA
   Name: api
   Value: 2001:4860:4802:36::15

   Type: AAAA
   Name: api
   Value: 2001:4860:4802:38::15
   ```

8. Click **Done**

### 2.2 Map Frontend Domain (words.parrotsoftware.com)

Repeat the same process for the frontend:

1. Click **Add Mapping** again
2. **Service**: Select `treatment-web`
3. **Region**: Same region as backend
4. **Subdomain**: Enter `words.parrotsoftware.com`
5. Note the DNS records (will be similar to backend)
6. Click **Done**

## Step 3: Configure DNS in GoDaddy

### 3.1 Access GoDaddy DNS Manager

1. Log in to [GoDaddy](https://www.godaddy.com)
2. Go to **My Products**
3. Find **Domains**
4. Click **DNS** next to `parrotsoftware.com`

### 3.2 Add DNS Records for Backend (api.parrotsoftware.com)

For each A record provided by Cloud Run:

1. Click **Add** (or **Add Record**)
2. Select record type: **A**
3. **Host**: `api`
4. **Points to**: Enter the IP address (e.g., `216.239.32.21`)
5. **TTL**: `600` seconds (or `1 Hour`)
6. Click **Save**

Repeat for all 4 A records.

For each AAAA record:

1. Click **Add**
2. Select record type: **AAAA**
3. **Host**: `api`
4. **Points to**: Enter the IPv6 address (e.g., `2001:4860:4802:32::15`)
5. **TTL**: `600` seconds
6. Click **Save**

Repeat for all 4 AAAA records.

### 3.3 Add DNS Records for Frontend (words.parrotsoftware.com)

Repeat the same process, but use:
- **Host**: `app` (instead of `api`)
- Same IP addresses from Cloud Run

### 3.4 Verify DNS Configuration

After adding all records, your DNS should have:

**For api.parrotsoftware.com**:
- 4 A records (all with host `api`)
- 4 AAAA records (all with host `api`)

**For words.parrotsoftware.com**:
- 4 A records (all with host `app`)
- 4 AAAA records (all with host `app`)

**Note**: GoDaddy allows multiple records with the same host name for redundancy.

## Step 4: Wait for DNS Propagation

### 4.1 Expected Wait Time

- **Minimum**: 15-30 minutes
- **Maximum**: 48 hours (rare)
- **Typical**: 1-4 hours

### 4.2 Check DNS Propagation

Use online tools to verify DNS has propagated:

**Method 1: DNS Checker**
1. Go to [https://dnschecker.org](https://dnschecker.org)
2. Enter `words.parrotsoftware.com`
3. Select record type: **A**
4. Click **Search**
5. Verify IP addresses match Cloud Run's values
6. Repeat for `api.parrotsoftware.com`

**Method 2: Command Line (Windows)**
```cmd
nslookup words.parrotsoftware.com
nslookup api.parrotsoftware.com
```

**Method 2: Command Line (Mac/Linux)**
```bash
dig words.parrotsoftware.com
dig api.parrotsoftware.com
```

Look for the IP addresses in the response.

## Step 5: Verify SSL Certificate

Cloud Run automatically provisions SSL certificates for custom domains.

### 5.1 Check Certificate Status

1. In Google Cloud Console, go to **Cloud Run** > **Manage Custom Domains**
2. Find your mappings for `words.parrotsoftware.com` and `api.parrotsoftware.com`
3. Check the **Certificate Status**:
   - ⏳ **Pending**: DNS not yet propagated or certificate provisioning in progress
   - ✅ **Active**: Certificate is active and HTTPS is working

**Note**: Certificate provisioning can take 15 minutes to several hours after DNS propagation.

### 5.2 Test HTTPS

Once certificate status shows **Active**:

1. Open browser and navigate to:
   - `https://api.parrotsoftware.com/health`
   - `https://words.parrotsoftware.com`

2. Verify:
   - ✅ Page loads over HTTPS
   - ✅ No SSL warnings
   - ✅ Lock icon appears in address bar

3. Click the lock icon to view certificate details:
   - Issued by: Google Trust Services
   - Valid for: `*.parrotsoftware.com` or specific subdomain

## Step 6: Update Environment Variables

### 6.1 Update Frontend Environment Variable

The frontend needs to know the backend API URL:

1. In Google Cloud Console, go to **Cloud Run**
2. Click on `treatment-web` service
3. Click **Edit & Deploy New Revision**
4. Scroll to **Environment variables**
5. Update or add:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://api.parrotsoftware.com`
6. Click **Deploy**

### 6.2 Update Backend CORS Settings

1. Click on `treatment-api` service
2. Click **Edit & Deploy New Revision**
3. Update environment variable:
   - **Name**: `ALLOWED_ORIGINS`
   - **Value**: `https://words.parrotsoftware.com,http://localhost:3000`
4. Click **Deploy**

## Step 7: Test the Deployed Application

### 7.1 Test Backend API

```bash
# Health check
curl https://api.parrotsoftware.com/health

# Expected response:
# {"status":"healthy"}
```

### 7.2 Test Frontend

1. Open `https://words.parrotsoftware.com` in browser
2. Verify the application loads
3. Test navigation and basic functionality

### 7.3 Test End-to-End Flow

1. Try signing up for an account
2. Check email for confirmation
3. Log in
4. Test the Word Finding or Life Words treatment app
5. Verify data is saved to Supabase

## Troubleshooting

### Domain Not Loading (404 Error)

**Problem**: `words.parrotsoftware.com` returns 404

**Solutions**:
1. Verify DNS records are correct (use dnschecker.org)
2. Check Cloud Run domain mapping exists
3. Wait for DNS propagation (can take up to 48 hours)
4. Verify service is running in Cloud Run

### SSL Certificate Pending

**Problem**: Certificate status stuck on "Pending"

**Solutions**:
1. Verify DNS records are correctly configured
2. Wait (can take several hours)
3. Check for DNS conflicts (remove old records)
4. Contact Google Cloud support if stuck for >24 hours

### Backend Connection Errors

**Problem**: Frontend can't connect to backend

**Solutions**:
1. Verify `NEXT_PUBLIC_API_URL` is set to `https://api.parrotsoftware.com`
2. Check CORS settings in backend allow frontend domain
3. Test backend directly: `curl https://api.parrotsoftware.com/health`
4. Check Cloud Run logs for errors

### 403 Forbidden Errors

**Problem**: Requests blocked with 403

**Solutions**:
1. Check Cloud Run service allows unauthenticated access:
   - Go to service in Cloud Run
   - Permissions tab
   - Ensure `allUsers` has `Cloud Run Invoker` role
2. Verify no Cloud Armor rules blocking traffic

## Monitoring and Maintenance

### View Logs

**Backend Logs**:
1. Go to **Cloud Run** > `treatment-api`
2. Click **Logs** tab
3. Filter by severity level

**Frontend Logs**:
1. Go to **Cloud Run** > `treatment-web`
2. Click **Logs** tab

### Monitor Performance

1. Go to **Cloud Run** service
2. Click **Metrics** tab
3. View:
   - Request count
   - Request latency
   - CPU utilization
   - Memory utilization

### Set Up Alerts

1. Go to **Monitoring** > **Alerting**
2. Click **Create Policy**
3. Configure alerts for:
   - High error rate (>5% of requests)
   - High latency (>2 seconds)
   - Service down

## Cost Monitoring

### Check Cloud Run Costs

1. Go to **Billing** > **Cost table**
2. Filter by:
   - **Service**: Cloud Run
   - **Project**: life-words-production
3. View costs by:
   - Service instance
   - Region
   - Time period

### Expected Costs (Low Traffic)

- **Cloud Run**: $0-5/month (free tier: 2M requests)
- **Speech-to-Text**: $6-12/month (60 min free, then $0.006/15s)
- **Text-to-Speech**: $0.40-8/month ($4-16 per 1M chars)
- **Total**: ~$6-25/month for low traffic

## Next Steps

After successful deployment:
1. Configure Supabase database: [06-supabase-setup.md](./06-supabase-setup.md)
2. Test all application features
3. Set up monitoring and alerts
4. Plan for future releases (v1.1.0, v1.2.0, etc.)

## Deployment Workflow Reference

For future deployments:

1. Make code changes locally
2. Test thoroughly
3. Commit and push to `main` branch
4. Create a new GitHub release with incremented version tag (e.g., `v1.0.1`, `v1.1.0`)
5. GitHub Actions automatically deploys
6. Verify deployment in Cloud Run
7. Test at `words.parrotsoftware.com`

**Rollback Process** (if needed):
1. Go to Cloud Run service
2. Click **Revisions** tab
3. Select previous working revision
4. Click **Serve this revision**
