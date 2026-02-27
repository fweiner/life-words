# PowerShell script to migrate secrets from GitHub to GCP Secret Manager
# Run this locally after authenticating with gcloud

$PROJECT_ID = "life-words-production"
$ENVIRONMENT = "production"

Write-Host "Migrating secrets to GCP Secret Manager for $PROJECT_ID..." -ForegroundColor Cyan

# Function to create or update a secret
function Sync-Secret {
    param(
        [string]$SecretName,
        [string]$SecretValue
    )

    if ([string]::IsNullOrWhiteSpace($SecretValue)) {
        Write-Host "Skipping $SecretName (value not provided)" -ForegroundColor Yellow
        return
    }

    # Check if secret exists
    $exists = gcloud secrets describe $SecretName --project=$PROJECT_ID 2>$null

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Creating $SecretName..." -ForegroundColor Green
        $SecretValue | gcloud secrets create $SecretName --project=$PROJECT_ID --replication-policy="automatic" --data-file=-
    } else {
        Write-Host "Updating $SecretName..." -ForegroundColor Yellow
        $SecretValue | gcloud secrets versions add $SecretName --project=$PROJECT_ID --data-file=-
    }
}

# Get secrets from GitHub CLI
Write-Host "`nFetching secrets from GitHub..." -ForegroundColor Cyan

$SUPABASE_URL = & gh secret list --json name,updatedAt | ConvertFrom-Json | Where-Object { $_.name -eq "SUPABASE_URL" }
$SUPABASE_SECRET_KEY = & gh secret list --json name,updatedAt | ConvertFrom-Json | Where-Object { $_.name -eq "SUPABASE_SECRET_KEY" }
$SUPABASE_ANON_KEY = & gh secret list --json name,updatedAt | ConvertFrom-Json | Where-Object { $_.name -eq "SUPABASE_ANON_KEY" }
$OPENAI_API_KEY = & gh secret list --json name,updatedAt | ConvertFrom-Json | Where-Object { $_.name -eq "OPENAI_API_KEY" }
$RESEND_API_KEY = & gh secret list --json name,updatedAt | ConvertFrom-Json | Where-Object { $_.name -eq "RESEND_API_KEY" }

Write-Host "`nNote: GitHub CLI cannot retrieve secret values for security." -ForegroundColor Yellow
Write-Host "Please provide the secret values when prompted.`n" -ForegroundColor Yellow

# Prompt for secret values
$SUPABASE_URL_VALUE = Read-Host "SUPABASE_URL"
$SUPABASE_SECRET_KEY_VALUE = Read-Host "SUPABASE_SECRET_KEY" -AsSecureString | ConvertFrom-SecureString -AsPlainText
$SUPABASE_ANON_KEY_VALUE = Read-Host "SUPABASE_ANON_KEY" -AsSecureString | ConvertFrom-SecureString -AsPlainText
$OPENAI_API_KEY_VALUE = Read-Host "OPENAI_API_KEY" -AsSecureString | ConvertFrom-SecureString -AsPlainText
$RESEND_API_KEY_VALUE = Read-Host "RESEND_API_KEY" -AsSecureString | ConvertFrom-SecureString -AsPlainText

Write-Host "`nCreating/updating secrets in GCP Secret Manager..." -ForegroundColor Cyan

# Create secrets with environment prefix
Sync-Secret "$ENVIRONMENT-supabase-url" $SUPABASE_URL_VALUE
Sync-Secret "$ENVIRONMENT-supabase-secret-key" $SUPABASE_SECRET_KEY_VALUE
Sync-Secret "$ENVIRONMENT-supabase-anon-key" $SUPABASE_ANON_KEY_VALUE
Sync-Secret "openai-api-key" $OPENAI_API_KEY_VALUE
Sync-Secret "resend-api-key" $RESEND_API_KEY_VALUE

Write-Host "`nGranting Secret Manager access to Cloud Run service account..." -ForegroundColor Cyan

# Get the default compute service account
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
$SERVICE_ACCOUNT = "$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

# Grant Secret Manager Secret Accessor role
$secrets = @(
    "$ENVIRONMENT-supabase-url",
    "$ENVIRONMENT-supabase-secret-key",
    "$ENVIRONMENT-supabase-anon-key",
    "openai-api-key",
    "resend-api-key"
)

foreach ($secret in $secrets) {
    $exists = gcloud secrets describe $secret --project=$PROJECT_ID 2>$null
    if ($LASTEXITCODE -eq 0) {
        gcloud secrets add-iam-policy-binding $secret `
            --project=$PROJECT_ID `
            --member="serviceAccount:$SERVICE_ACCOUNT" `
            --role="roles/secretmanager.secretAccessor" `
            --quiet 2>$null
        Write-Host "Granted access to $secret" -ForegroundColor Green
    }
}

Write-Host "`n✅ Secrets migration complete!" -ForegroundColor Green
Write-Host "`nSecrets created:" -ForegroundColor Cyan
gcloud secrets list --project=$PROJECT_ID --filter="name~$ENVIRONMENT-"
