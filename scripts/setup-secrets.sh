#!/bin/bash
set -e

# Script to set up secrets in GCP Secret Manager
# Run this locally to migrate from GitHub Secrets to Secret Manager

PROJECT_ID="life-words-production"
ENVIRONMENT="production"

echo "Setting up secrets in GCP Secret Manager for $PROJECT_ID..."

# Helper function to create or update a secret
sync_secret() {
  local secret_name="$1"
  local secret_value="$2"

  if [[ -z "$secret_value" ]]; then
    echo "Skipping $secret_name (value not provided)"
    return
  fi

  if ! gcloud secrets describe "$secret_name" --project="$PROJECT_ID" &>/dev/null; then
    echo "Creating $secret_name..."
    echo -n "$secret_value" | gcloud secrets create "$secret_name" \
      --project="$PROJECT_ID" \
      --replication-policy="automatic" \
      --data-file=-
  else
    # Check if current value matches
    current_value=$(gcloud secrets versions access latest --secret="$secret_name" --project="$PROJECT_ID" 2>/dev/null || echo "")
    if [[ "$current_value" == "$secret_value" ]]; then
      echo "$secret_name unchanged, skipping..."
    else
      echo "Updating $secret_name..."
      echo -n "$secret_value" | gcloud secrets versions add "$secret_name" \
        --project="$PROJECT_ID" \
        --data-file=-
    fi
  fi
}

# Prompt for secrets (you can also pass them as env vars)
echo ""
echo "Please provide the following secret values:"
echo "(Press Enter to skip any secret)"
echo ""

read -p "SUPABASE_URL: " SUPABASE_URL
read -p "SUPABASE_SECRET_KEY: " -s SUPABASE_SECRET_KEY; echo
read -p "SUPABASE_ANON_KEY: " -s SUPABASE_ANON_KEY; echo
read -p "OPENAI_API_KEY: " -s OPENAI_API_KEY; echo
read -p "RESEND_API_KEY: " -s RESEND_API_KEY; echo

echo ""
echo "Creating/updating secrets..."

# Create environment-prefixed secrets
sync_secret "${ENVIRONMENT}-supabase-url" "$SUPABASE_URL"
sync_secret "${ENVIRONMENT}-supabase-secret-key" "$SUPABASE_SECRET_KEY"
sync_secret "${ENVIRONMENT}-supabase-anon-key" "$SUPABASE_ANON_KEY"
sync_secret "openai-api-key" "$OPENAI_API_KEY"
sync_secret "resend-api-key" "$RESEND_API_KEY"

echo ""
echo "Granting Secret Manager access to Cloud Run service account..."

# Get the default compute service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant Secret Manager Secret Accessor role
for secret in "${ENVIRONMENT}-supabase-url" "${ENVIRONMENT}-supabase-secret-key" "${ENVIRONMENT}-supabase-anon-key" "openai-api-key" "resend-api-key"; do
  if gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
    gcloud secrets add-iam-policy-binding "$secret" \
      --project="$PROJECT_ID" \
      --member="serviceAccount:${SERVICE_ACCOUNT}" \
      --role="roles/secretmanager.secretAccessor" \
      --quiet || true
    echo "Granted access to $secret"
  fi
done

echo ""
echo "✅ Secrets setup complete!"
echo ""
echo "Secrets created:"
gcloud secrets list --project="$PROJECT_ID" --filter="name~${ENVIRONMENT}-"
