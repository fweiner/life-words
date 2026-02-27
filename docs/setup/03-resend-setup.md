# Resend Email Service Setup Guide

This guide walks you through setting up Resend for sending emails in the Life Words application, including integration with Supabase authentication.

## Prerequisites

- A domain name (parrotsoftware.com)
- Access to your domain's DNS settings (GoDaddy)

## Step 1: Create Resend Account

### 1.1 Sign Up

1. Navigate to [https://resend.com](https://resend.com)
2. Click **Sign up**
3. Sign up with:
   - Email address
   - GitHub account (recommended)
4. Verify your email address

### 1.2 Complete Onboarding

1. Enter your name and company information
2. Select your use case: **Transactional emails**
3. Click **Continue**

## Step 2: Verify Your Domain

### 2.1 Add Domain in Resend

1. In the Resend dashboard, go to **Domains**
2. Click **+ Add Domain**
3. Enter your domain: `parrotsoftware.com`
4. Click **Add**

### 2.2 Configure DNS Records in GoDaddy

Resend will provide you with DNS records to add. You'll need to add these to your GoDaddy DNS settings.

**DNS Records to Add:**

1. **SPF Record** (TXT)
   - Type: `TXT`
   - Name: `@` (or leave blank, depending on GoDaddy's interface)
   - Value: `v=spf1 include:resend.com ~all`
   - TTL: `600` (or default)

2. **DKIM Record** (TXT)
   - Type: `TXT`
   - Name: `resend._domainkey` (Resend will provide the exact value)
   - Value: (Long string provided by Resend, starts with `p=`)
   - TTL: `600`

3. **Custom Return-Path** (CNAME) - Optional but recommended
   - Type: `CNAME`
   - Name: `resend`
   - Value: `resend.com`
   - TTL: `600`

### 2.3 Add DNS Records in GoDaddy

1. Log in to your [GoDaddy account](https://www.godaddy.com)
2. Go to **My Products**
3. Find **Domains** and click **DNS** next to `parrotsoftware.com`
4. Scroll to the **Records** section
5. For each DNS record above:
   - Click **Add** (or **Add Record**)
   - Select the record **Type**
   - Enter the **Name** (host)
   - Enter the **Value** (data/points to)
   - Set the **TTL**
   - Click **Save**

### 2.4 Verify Domain in Resend

1. Return to the Resend dashboard
2. Click **Verify DNS Records**
3. Wait for verification (can take 15 minutes to 48 hours)
4. Status should change from "Pending" to "Verified"

**Troubleshooting Verification:**
- DNS changes can take up to 48 hours to propagate
- Use [https://dnschecker.org](https://dnschecker.org) to check if DNS records have propagated
- Ensure you entered the records exactly as shown in Resend

## Step 3: Create API Key

### 3.1 Generate API Key

1. In the Resend dashboard, go to **API Keys**
2. Click **+ Create API Key**
3. API Key details:
   - **Name**: `Life Words - Production`
   - **Permission**: **Full Access** (or **Sending access** for production)
   - **Domain**: Select `parrotsoftware.com`
4. Click **Create**

### 3.2 Save Your API Key

**IMPORTANT**: You'll only see the API key once!

1. Copy the API key (starts with `re_`)
2. Save it immediately to a secure location:
   - Password manager (recommended)
   - Encrypted notes app
3. Click **Done**

### 3.3 Create Development API Key (Optional)

For local development, you may want a separate key:

1. Click **+ Create API Key** again
2. Name: `Life Words - Development`
3. Permission: **Full Access**
4. Domain: `parrotsoftware.com`
5. Click **Create** and save the key

## Step 4: Add API Key to Environment Variables

### 4.1 For Local Development (Backend)

1. Open `backend/.env`:
   ```bash
   cd backend
   nano .env  # or use your preferred editor
   ```

2. Add your Resend API key:
   ```env
   RESEND_API_KEY=re_your_actual_key_here
   ```

3. Save the file

### 4.2 For GitHub Secrets (Production)

1. Navigate to your GitHub repository
2. Go to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `RESEND_API_KEY`
5. Value: Paste your production API key
6. Click **Add secret**

See [04-github-secrets.md](./04-github-secrets.md) for more details.

## Step 5: Configure Supabase to Use Resend

### 5.1 Access Supabase Project Settings

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Select your project: `ciqrtvuxalpnjjsmrmwc`
3. Go to **Project Settings** (gear icon)
4. Select **Auth** in the left sidebar

### 5.2 Configure SMTP Settings

1. Scroll to **SMTP Settings**
2. Toggle **Enable Custom SMTP** to ON
3. Enter the following details:

   - **Sender email**: `noreply@parrotsoftware.com`
   - **Sender name**: `Life Words`
   - **Host**: `smtp.resend.com`
   - **Port number**: `587`
   - **Username**: `resend`
   - **Password**: Your Resend API key (the one starting with `re_`)

4. Click **Save**

### 5.3 Test Email Configuration

1. Scroll down to **Email Templates** in the Supabase Auth settings
2. Click on **Confirm signup**
3. You'll see a preview of the email template
4. (Optional) Customize the template if needed
5. Send a test email by creating a test user account

## Step 6: Configure Email Templates (Optional)

### 6.1 Customize Supabase Email Templates

In Supabase Auth settings, you can customize:

1. **Confirm signup** - Email verification
2. **Invite user** - User invitations
3. **Magic link** - Passwordless login (if using)
4. **Change email address** - Email change confirmation
5. **Reset password** - Password reset

**Template Variables Available:**
- `{{ .ConfirmationURL }}` - Confirmation link
- `{{ .Token }}` - Verification token
- `{{ .TokenHash }}` - Hashed token
- `{{ .SiteURL }}` - Your app URL

### 6.2 Example Custom Template

```html
<h2>Welcome to Life Words</h2>
<p>Thank you for signing up! Please confirm your email address by clicking the link below:</p>
<p><a href="{{ .ConfirmationURL }}">Confirm Email Address</a></p>
<p>This link will expire in 24 hours.</p>
<p>If you didn't create an account, you can safely ignore this email.</p>
```

## Step 7: Test Email Sending

### 7.1 Test from Supabase

1. Create a test user in Supabase:
   - Go to **Authentication** > **Users**
   - Click **Add user** > **Create new user**
   - Enter a test email address
   - Check the "Auto Confirm User" option (for initial test)
   - Click **Create user**

2. Try the password reset flow:
   - Go to the login page of your app (when implemented)
   - Click "Forgot password"
   - Enter the test email
   - Check your inbox for the reset email

### 7.2 Test from Backend Code

Once your backend is implemented, you can test programmatically:

```python
from resend import Resend

resend = Resend(api_key="re_your_key_here")

params = {
    "from": "noreply@parrotsoftware.com",
    "to": ["test@example.com"],
    "subject": "Test Email",
    "html": "<strong>Hello from Life Words!</strong>"
}

email = resend.emails.send(params)
print(email)
```

## Cost Information

### Resend Pricing

**Free Tier:**
- 3,000 emails per month
- 100 emails per day
- Perfect for development and small-scale production

**Paid Plans:**
- $20/month for 50,000 emails
- $80/month for 200,000 emails
- Custom pricing for higher volumes

**For this application:**
- Estimated 100-500 emails/month (authentication + notifications)
- **Free tier is sufficient**

## Monitoring Email Delivery

### 7.1 View Email Logs

1. In Resend dashboard, go to **Logs**
2. View all sent emails with:
   - Delivery status
   - Open rates (if tracking enabled)
   - Click rates
   - Bounce/complaint notifications

### 7.2 Set Up Webhooks (Optional)

To receive real-time notifications about email events:

1. Go to **Webhooks** in Resend dashboard
2. Click **+ Add Endpoint**
3. Enter your webhook URL (e.g., `https://api.parrotsoftware.com/webhooks/resend`)
4. Select events to subscribe to:
   - `email.sent`
   - `email.delivered`
   - `email.bounced`
   - `email.complained`
5. Click **Add**

## Troubleshooting

### Emails Not Sending

1. **Check domain verification**:
   - Ensure domain is verified in Resend dashboard
   - Verify DNS records are correct using `nslookup` or dnschecker.org

2. **Check API key**:
   - Ensure API key is correct and not expired
   - Verify you're using the production key in production

3. **Check Supabase SMTP settings**:
   - Host: `smtp.resend.com`
   - Port: `587`
   - Username: `resend`
   - Password: Your Resend API key

### Emails Going to Spam

1. **SPF/DKIM**: Ensure all DNS records are properly configured
2. **Sender reputation**: Use a verified domain, not a free email provider
3. **Email content**: Avoid spam trigger words, use plain text alternative
4. **Warm up your domain**: Start with low volume and gradually increase

### Domain Verification Failing

1. **Wait**: DNS propagation can take up to 48 hours
2. **Check DNS records**: Use [https://mxtoolbox.com/SuperTool.aspx](https://mxtoolbox.com/SuperTool.aspx)
3. **Verify exact values**: Ensure no extra spaces or characters
4. **Contact support**: Resend has excellent support via email

## Security Best Practices

1. **Protect API keys**:
   - Never commit to Git
   - Use environment variables
   - Rotate keys periodically

2. **Use separate keys for environments**:
   - Development
   - Staging
   - Production

3. **Monitor usage**:
   - Set up alerts for unusual activity
   - Review logs regularly

4. **Implement rate limiting**:
   - Prevent abuse of email sending
   - Set limits on password reset attempts

## Next Steps

After setting up Resend:
1. Configure GitHub secrets: [04-github-secrets.md](./04-github-secrets.md)
2. Set up Supabase database: [06-supabase-setup.md](./06-supabase-setup.md)
3. Test authentication flows with email confirmation
