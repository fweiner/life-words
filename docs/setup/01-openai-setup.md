# OpenAI API Setup Guide

This guide walks you through creating an OpenAI API key for the Life Words application.

## Prerequisites

- A credit card for billing (OpenAI requires payment information)
- An email address

## Step-by-Step Instructions

### 1. Create an OpenAI Account

1. Navigate to [https://platform.openai.com](https://platform.openai.com)
2. Click **Sign up** in the top right corner
3. Choose to sign up with:
   - Email address
   - Google account
   - Microsoft account
4. Complete the verification process

### 2. Add Billing Information

1. Once logged in, click your profile icon in the top right
2. Select **Settings** from the dropdown
3. Navigate to **Billing** in the left sidebar
4. Click **Add payment method**
5. Enter your credit card information
6. Click **Save**

### 3. Set Up Usage Limits (Recommended)

To control costs and prevent unexpected charges:

1. In the Billing section, find **Usage limits**
2. Set a **Hard limit** (e.g., $50/month)
   - Once this limit is reached, API requests will be rejected
3. Set a **Soft limit** (e.g., $30/month)
   - You'll receive an email notification when this is reached
4. Click **Save**

### 4. Create an API Key

1. Click on **API keys** in the left sidebar (or navigate to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys))
2. Click **+ Create new secret key**
3. Give your key a descriptive name:
   - For local development: `Treatment App - Development`
   - For production: `Treatment App - Production`
4. (Optional) Set permissions:
   - For this project, you can leave the default "All" permissions
5. Click **Create secret key**

### 5. Save Your API Key

**IMPORTANT**: You'll only see the API key once!

1. Copy the API key that appears (starts with `sk-proj-...`)
2. Save it immediately to a secure location:
   - Password manager (recommended)
   - Encrypted notes app
3. Click **Done**

### 6. Add to Environment Variables

#### For Local Development

1. In the project backend directory, create a `.env` file if it doesn't exist:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Open `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

3. Save the file

#### For GitHub Secrets (Production)

1. Navigate to your GitHub repository
2. Go to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `OPENAI_API_KEY`
5. Value: Paste your API key
6. Click **Add secret**

See [04-github-secrets.md](./04-github-secrets.md) for more details.

## Verifying Your Setup

To verify your API key is working:

1. Start the backend server:
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload
   ```

2. The server should start without errors related to OpenAI

## Cost Management

### Understanding Pricing

For this project, we're using **GPT-4o-mini**:
- Input: $0.150 per 1M tokens (~$0.000150 per 1K tokens)
- Output: $0.600 per 1M tokens (~$0.000600 per 1K tokens)

**Estimated costs for typical usage:**
- Single AI interaction (100 tokens input, 200 tokens output): ~$0.00015
- 1,000 interactions: ~$0.15
- 10,000 interactions: ~$1.50

### Monitoring Usage

1. Go to [https://platform.openai.com/usage](https://platform.openai.com/usage)
2. View your current month's usage
3. Set up email notifications for usage alerts

## Troubleshooting

### "Invalid API key" Error

- Verify you copied the complete key (including `sk-proj-` prefix)
- Check for extra spaces or line breaks
- Ensure the key is active (not revoked) in the OpenAI dashboard

### "Insufficient quota" Error

- Add payment method in billing settings
- Check your usage limits haven't been exceeded
- Verify your credit card is valid and has available funds

### Rate Limit Errors

If you see rate limit errors:
- Default limit for GPT-4o-mini: 500,000 tokens/minute
- If needed, request a limit increase in your OpenAI account settings

## Security Best Practices

1. **Never commit API keys to Git**
   - The `.gitignore` file already excludes `.env` files
   - Double-check before committing

2. **Use different keys for development and production**
   - Easier to track usage
   - Can revoke one without affecting the other

3. **Rotate keys periodically**
   - Create a new key every 3-6 months
   - Delete old keys after migration

4. **Monitor usage regularly**
   - Check the OpenAI dashboard weekly
   - Set up usage alerts

## Next Steps

After setting up OpenAI:
1. Set up Google Cloud Platform: [02-gcp-setup.md](./02-gcp-setup.md)
2. Configure Resend for emails: [03-resend-setup.md](./03-resend-setup.md)
