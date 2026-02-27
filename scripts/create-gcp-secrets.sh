#!/bin/bash
set -e

# Script to create GCP secrets from values
# You'll need to provide the actual secret values when prompted

PROJECT_ID="life-words-production"
ENVIRONMENT="production"

echo "Creating secrets in GCP Secret Manager for $PROJECT_ID..."
echo ""

# Function to create or update a secret
create_or_update_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [[ -z "$secret_value" ]]; then
        echo "Skipping $secret_name (no value provided)"
        return
    fi

    if ! gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
        echo "Creating $secret_name..."
        echo -n "$secret_value" | gcloud secrets create "$secret_name" \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" \
            --data-file=-
    else
        echo "Updating $secret_name..."
        echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
            --project="$PROJECT_ID" \
            --data-file=-
    fi
}

# Known values
SUPABASE_URL="https://nnvqtxwobvyitqbsdskc.supabase.co"

echo "Please enter the following secret values:"
echo "(These should match your GitHub secrets)"
echo ""

read -p "SUPABASE_SECRET_KEY: " -s SUPABASE_SECRET_KEY; echo
read -p "SUPABASE_ANON_KEY: " -s SUPABASE_ANON_KEY; echo
read -p "OPENAI_API_KEY: " -s OPENAI_API_KEY; echo
read -p "RESEND_API_KEY (or press Enter to skip): " -s RESEND_API_KEY; echo

echo ""
echo "Creating secrets..."

# Create secrets
create_or_update_secret "${ENVIRONMENT}-supabase-url" "$SUPABASE_URL"
create_or_update_secret "${ENVIRONMENT}-supabase-secret-key" "$SUPABASE_SECRET_KEY"
create_or_update_secret "${ENVIRONMENT}-supabase-anon-key" "$SUPABASE_ANON_KEY"
create_or_update_secret "openai-api-key" "$OPENAI_API_KEY"
create_or_update_secret "resend-api-key" "$RESEND_API_KEY"

echo ""
echo "Granting access to Cloud Run service account..."

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant access to each secret
for secret in "${ENVIRONMENT}-supabase-url" "${ENVIRONMENT}-supabase-secret-key" "${ENVIRONMENT}-supabase-anon-key" "openai-api-key" "resend-api-key"; do
    if gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
        gcloud secrets add-iam-policy-binding "$secret" \
            --project="$PROJECT_ID" \
            --member="serviceAccount:${SERVICE_ACCOUNT}" \
            --role="roles/secretmanager.secretAccessor" \
            --quiet || true
        echo "✓ Granted access to $secret"
    fi
done

echo ""
echo "✅ Done! Secrets created:"
gcloud secrets list --project="$PROJECT_ID"
