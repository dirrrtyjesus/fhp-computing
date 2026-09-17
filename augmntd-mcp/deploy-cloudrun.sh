#!/usr/bin/env bash
# ==============================================================================
# augLABS augmntd MCP (Xenware) - Google Cloud Run Deployment Script
# Architecture Standard: augLABS augmntd MCP (Xenware) Enterprise Harmonic Bridge
# Deployment Reference: augmntdMCPdeployment.md
# ==============================================================================

set -euo pipefail

# Ensure Resource Attribution
export CLOUDSDK_METRICS_ENVIRONMENT="datacloud.antigravity"

SERVICE_NAME="${SERVICE_NAME:-augmntd-mcp-bridge}"
REGION="${REGION:-us-east1}"
PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "")}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

if [ -z "$PROJECT_ID" ]; then
  echo "Error: PROJECT_ID is not set and could not be determined from gcloud config."
  echo "Usage: PROJECT_ID=my-gcp-project ./deploy-cloudrun.sh"
  exit 1
fi

IMAGE_URI="gcr.io/${PROJECT_ID}/augmntd-mcp:${IMAGE_TAG}"

echo "=================================================================="
echo " Deploying augLABS augmntd MCP (Xenware) to Google Cloud Run"
echo " Project:     $PROJECT_ID"
echo " Service:     $SERVICE_NAME"
echo " Region:      $REGION"
echo " Image:       $IMAGE_URI"
echo " Attribution: $CLOUDSDK_METRICS_ENVIRONMENT"
echo "=================================================================="

# 1. Build and Submit Container Image to Google Container Registry / Artifact Registry
echo "[1/2] Building container image via Cloud Build..."
gcloud builds submit --tag "$IMAGE_URI" .

# 2. Deploy to Google Cloud Run with production flags
# Note:
# - timeout 3600 (60 mins) to support long-lived SSE connections and WebSockets
# - no-cpu-throttling keeps background tau_k clock and CDT state active outside requests
# - min-instances 1 eliminates cold starts for agent tool latency
# - concurrency 80 for multi-agent swarm capacity
echo "[2/2] Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_URI" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 3600 \
  --concurrency 80 \
  --min-instances 1 \
  --cpu 1 \
  --memory 1Gi \
  --no-cpu-throttling

echo "=================================================================="
echo " Deployment Complete!"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)')
echo " Service URL: $SERVICE_URL"
echo " Health Probe: $SERVICE_URL/healthz"
echo " MCP SSE:     $SERVICE_URL/sse"
echo " WSS Stream:  wss://${SERVICE_URL#https://}/tauk-stream"
echo "=================================================================="
