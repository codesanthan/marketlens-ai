#!/usr/bin/env bash
set -euo pipefail
: "${PROJECT_ID:?Set PROJECT_ID}"
REGION="${REGION:-us-central1}"
REPOSITORY="${REPOSITORY:-marketlens}"
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com logging.googleapis.com monitoring.googleapis.com iamcredentials.googleapis.com
gcloud artifacts repositories describe "$REPOSITORY" --location "$REGION" >/dev/null 2>&1 || gcloud artifacts repositories create "$REPOSITORY" --repository-format docker --location "$REGION"
for service in web api; do
  account="marketlens-${service}"
  gcloud iam service-accounts describe "${account}@${PROJECT_ID}.iam.gserviceaccount.com" >/dev/null 2>&1 || gcloud iam service-accounts create "$account" --display-name "MarketLens ${service} runtime"
done
# Runtime accounts receive no project-wide roles. Cloud Run automatically writes logs and metrics.
gcloud secrets describe marketlens-placeholder >/dev/null 2>&1 || printf 'replace-me' | gcloud secrets create marketlens-placeholder --data-file=-

