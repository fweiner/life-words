# Supabase Database Setup Guide

This guide walks you through configuring your Supabase database for the Life Words application, including cleaning up existing tables, creating the new schema, and setting up authentication.

## Prerequisites

- Access to Supabase project: `nnvqtxwobvyitqbsdskc`
- Supabase CLI installed (optional, for migrations)
- Completed Resend setup ([03-resend-setup.md](./03-resend-setup.md))

## Step 1: Access Your Supabase Project

1. Navigate to [https://app.supabase.com](https://app.supabase.com)
2. Sign in to your account
3. Select your project: `nnvqtxwobvyitqbsdskc`

## Step 2: Clean Up Existing Tables

⚠️ **WARNING**: This will delete existing data. Make backups if needed.

### 2.1 List Existing Tables

1. Go to **Table Editor** in the left sidebar
2. Review all existing tables
3. Note any tables you want to keep (unlikely for this fresh start)

### 2.2 Delete or Rename Existing Tables

**Option A: Delete Tables** (recommended for clean start)

For each table you want to remove:
1. Click on the table name
2. Click the **⋮** (three dots menu)
3. Select **Delete table**
4. Confirm deletion

**Option B: Rename Tables** (if you want to keep old data)

For each table:
1. Click on the table name
2. Click the **⋮** menu
3. Select **Edit table**
4. Rename to `old_[tablename]` (e.g., `old_users`)
5. Click **Save**

## Step 3: Create Database Schema

We'll create the database schema for the application. You can do this via the Supabase UI or SQL editor.

### 3.1 Open SQL Editor

1. Go to **SQL Editor** in the left sidebar
2. Click **+ New query**

### 3.2 Create Profiles Table

This table extends the auth.users table with additional user information.

```sql
-- Create profiles table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    date_of_birth DATE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS profiles_email_idx ON public.profiles(email);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for profiles
-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE
    USING (auth.uid() = id);

-- Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT
    WITH CHECK (auth.uid() = id);
```

Click **Run** (or press F5) to execute.

### 3.3 Create Treatment Sessions Table

```sql
-- Create treatment_sessions table
CREATE TABLE IF NOT EXISTS public.treatment_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    treatment_type TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMPTZ,
    data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS treatment_sessions_user_id_idx ON public.treatment_sessions(user_id);
CREATE INDEX IF NOT EXISTS treatment_sessions_treatment_type_idx ON public.treatment_sessions(treatment_type);
CREATE INDEX IF NOT EXISTS treatment_sessions_created_at_idx ON public.treatment_sessions(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.treatment_sessions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own sessions
CREATE POLICY "Users can view own sessions" ON public.treatment_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own sessions
CREATE POLICY "Users can insert own sessions" ON public.treatment_sessions
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own sessions
CREATE POLICY "Users can update own sessions" ON public.treatment_sessions
    FOR UPDATE
    USING (auth.uid() = user_id);
```

Click **Run** to execute.

### 3.4 Create Treatment Results Table

```sql
-- Create treatment_results table
CREATE TABLE IF NOT EXISTS public.treatment_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.treatment_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    score INTEGER,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS treatment_results_session_id_idx ON public.treatment_results(session_id);
CREATE INDEX IF NOT EXISTS treatment_results_user_id_idx ON public.treatment_results(user_id);
CREATE INDEX IF NOT EXISTS treatment_results_created_at_idx ON public.treatment_results(created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.treatment_results ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own results
CREATE POLICY "Users can view own results" ON public.treatment_results
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own results
CREATE POLICY "Users can insert own results" ON public.treatment_results
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

Click **Run** to execute.

### 3.5 Create User Progress Table

```sql
-- Create user_progress table
CREATE TABLE IF NOT EXISTS public.user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    treatment_type TEXT NOT NULL,
    total_sessions INTEGER DEFAULT 0 NOT NULL,
    average_score NUMERIC,
    last_session_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(user_id, treatment_type)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS user_progress_user_id_idx ON public.user_progress(user_id);
CREATE INDEX IF NOT EXISTS user_progress_treatment_type_idx ON public.user_progress(treatment_type);

-- Enable Row Level Security
ALTER TABLE public.user_progress ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can view their own progress
CREATE POLICY "Users can view own progress" ON public.user_progress
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can update their own progress
CREATE POLICY "Users can update own progress" ON public.user_progress
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can insert their own progress
CREATE POLICY "Users can insert own progress" ON public.user_progress
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);
```

Click **Run** to execute.

### 3.6 Create Triggers for Automatic Updates

```sql
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for profiles table
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_progress table
CREATE TRIGGER update_user_progress_updated_at
    BEFORE UPDATE ON public.user_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile when user signs up
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
```

Click **Run** to execute.

## Step 4: Verify Schema

### 4.1 Check Tables

Go to **Table Editor** and verify you see:
- ✅ profiles
- ✅ treatment_sessions
- ✅ treatment_results
- ✅ user_progress

### 4.2 Check RLS Policies

For each table:
1. Click on the table
2. Look for the 🔒 lock icon (indicates RLS is enabled)
3. Click the table → **Policies** tab
4. Verify policies exist

## Step 5: Create Storage Buckets

### 5.1 Create Treatment Images Bucket

1. Go to **Storage** in the left sidebar
2. Click **New bucket**
3. Bucket details:
   - **Name**: `treatment-images`
   - **Public bucket**: ✅ (checked)
4. Click **Create bucket**

### 5.2 Create User Uploads Bucket

1. Click **New bucket** again
2. Bucket details:
   - **Name**: `user-uploads`
   - **Public bucket**: ❌ (unchecked - private)
3. Click **Create bucket**

### 5.3 Configure Storage Policies

For **user-uploads** bucket:

1. Click on `user-uploads` bucket
2. Go to **Policies** tab
3. Click **New policy**
4. Use the policy builder or SQL:

```sql
-- Policy: Users can upload their own files
CREATE POLICY "Users can upload own files" ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'user-uploads' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can view their own files
CREATE POLICY "Users can view own files" ON storage.objects
    FOR SELECT
    USING (
        bucket_id = 'user-uploads' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can update their own files
CREATE POLICY "Users can update own files" ON storage.objects
    FOR UPDATE
    USING (
        bucket_id = 'user-uploads' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy: Users can delete their own files
CREATE POLICY "Users can delete own files" ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'user-uploads' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );
```

## Step 6: Configure Authentication

### 6.1 Enable Email/Password Authentication

1. Go to **Authentication** > **Providers**
2. Find **Email** provider
3. Ensure it's **Enabled**
4. Configuration:
   - **Confirm email**: ✅ (recommended - enabled)
   - **Secure email change**: ✅ (enabled)
   - **Secure password change**: ✅ (enabled)

### 6.2 Configure Email Templates

1. Go to **Authentication** > **Email Templates**

2. **Confirm Signup** template:
   ```html
   <h2>Welcome to Life Words</h2>
   <p>Thank you for signing up! Please confirm your email address by clicking the link below:</p>
   <p><a href="{{ .ConfirmationURL }}">Confirm Email Address</a></p>
   <p>This link will expire in 24 hours.</p>
   <p>If you didn't create an account, you can safely ignore this email.</p>
   ```

3. **Reset Password** template:
   ```html
   <h2>Reset Your Password</h2>
   <p>We received a request to reset your password. Click the link below to create a new password:</p>
   <p><a href="{{ .ConfirmationURL }}">Reset Password</a></p>
   <p>This link will expire in 1 hour.</p>
   <p>If you didn't request this, you can safely ignore this email.</p>
   ```

4. Click **Save** for each template

### 6.3 Configure Site URL

1. Go to **Authentication** > **URL Configuration**
2. **Site URL**: `https://words.parrotsoftware.com`
3. **Redirect URLs**: Add:
   - `https://words.parrotsoftware.com/**`
   - `http://localhost:3000/**` (for development)
4. Click **Save**

### 6.4 Configure Email Rate Limiting

1. Go to **Authentication** > **Rate Limits**
2. Recommended settings:
   - **Sign up**: 5 requests per hour
   - **Sign in**: 10 requests per hour
   - **Password recovery**: 3 requests per hour

## Step 7: Get API Keys

### 7.1 Find Your Project Keys

1. Go to **Project Settings** (gear icon) > **API**
2. Note the following keys:

**Project URL**:
```
https://nnvqtxwobvyitqbsdskc.supabase.co
```

**API Keys**:
- **anon/public key** (publishable key):
  - Use in frontend (`NEXT_PUBLIC_SUPABASE_ANON_KEY`)
  - Safe to expose in client-side code

- **service_role key** (secret key):
  - Use in backend (`SUPABASE_SECRET_KEY`)
  - ⚠️ **Never expose in frontend**
  - Has admin privileges

### 7.2 Add Keys to Environment Files

**Backend** (`backend/.env`):
```env
SUPABASE_URL=https://nnvqtxwobvyitqbsdskc.supabase.co
SUPABASE_SECRET_KEY=your-service-role-key-here
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_SUPABASE_URL=https://nnvqtxwobvyitqbsdskc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**GitHub Secrets**:
- Add `SUPABASE_URL`
- Add `SUPABASE_ANON_KEY`
- Add `SUPABASE_SECRET_KEY`

(See [04-github-secrets.md](./04-github-secrets.md))

## Step 8: Test Database Connection

### 8.1 Test from SQL Editor

```sql
-- Test query
SELECT * FROM public.profiles LIMIT 1;

-- Should return empty result (no rows) if fresh database
-- Should NOT return permission error
```

### 8.2 Test from Local Backend

Once backend is implemented, test connection:

```bash
cd backend
uv run python -c "
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SECRET_KEY')

headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}'
}

response = httpx.get(f'{url}/rest/v1/profiles', headers=headers)
print(f'Status: {response.status_code}')
print(f'Response: {response.text}')
"
```

Should return: `Status: 200` and `Response: []`

## Step 9: Create Test User

### 9.1 Manual Test User Creation

1. Go to **Authentication** > **Users**
2. Click **Add user** > **Create new user**
3. Enter:
   - **Email**: `test@example.com`
   - **Password**: `TestPassword123!`
   - **Auto Confirm User**: ✅ (checked, for testing)
4. Click **Create user**

### 9.2 Verify Profile Created

1. Go to **Table Editor** > **profiles**
2. You should see a new row with the test user's email
3. This confirms the trigger is working

## Troubleshooting

### RLS Policy Errors

**Problem**: "new row violates row-level security policy"

**Solutions**:
1. Verify RLS policies are created correctly
2. Check that `auth.uid()` is being set properly
3. Ensure user is authenticated when making requests

### Trigger Not Creating Profile

**Problem**: Profile not automatically created on signup

**Solutions**:
1. Verify trigger exists:
   ```sql
   SELECT * FROM pg_trigger WHERE tgname = 'on_auth_user_created';
   ```
2. Check function exists:
   ```sql
   SELECT * FROM pg_proc WHERE proname = 'handle_new_user';
   ```
3. Recreate trigger (see Step 3.6)

### Storage Policy Issues

**Problem**: Can't upload files to storage

**Solutions**:
1. Verify bucket exists and is configured correctly
2. Check storage policies allow the operation
3. Ensure file path matches policy structure (user-uploads/USER_ID/file.jpg)

## Database Maintenance

### Regular Backups

Supabase automatically backs up your database, but you can also:

1. Go to **Database** > **Backups**
2. View automatic backups
3. Manual backup: Use `pg_dump` via SQL Editor or CLI

### Monitor Database Size

1. Go to **Reports** > **Database**
2. View:
   - Database size
   - Table sizes
   - Index sizes

### Optimize Performance

```sql
-- View slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- Analyze table statistics
ANALYZE public.treatment_sessions;
ANALYZE public.treatment_results;
```

## Next Steps

After setting up Supabase:
1. Implement backend database layer
2. Implement authentication system
3. Test user signup/login flow
4. Begin implementing treatment apps

## Quick Reference

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `profiles` | User information | id, email, full_name |
| `treatment_sessions` | Individual sessions | user_id, treatment_type, data |
| `treatment_results` | Session outcomes | session_id, score, details |
| `user_progress` | Aggregated progress | user_id, treatment_type, total_sessions |

| Bucket | Public? | Purpose |
|--------|---------|---------|
| `treatment-images` | ✅ Yes | Public images for UI |
| `user-uploads` | ❌ No | User-specific files |
