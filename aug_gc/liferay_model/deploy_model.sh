#!/usr/bin/env bash
# Idempotent deploy script for the Liferay Model custom architecture.
# Usage:
#   ./deploy_model.sh                  # → model named "liferay" under your HF account
#   ./deploy_model.sh my-model-name    # → custom model name
#
set -euo pipefail

cd "$(dirname "$0")"

# Ensure the hf CLI is present
if ! command -v hf >/dev/null 2>&1; then
  echo "→ installing the hf CLI…"
  curl -LsSf https://hf.co/cli/install.sh | bash -s
  export PATH="$HOME/.local/bin:$PATH"
fi

# Resolve the target model ID (owner/repo)
if [[ -n "${MODEL:-}" ]]; then
  REPO="$MODEL"
else
  NAME="${1:-liferay}"
  USER="$(hf auth whoami 2>/dev/null | head -1 || true)"
  USER="${USER#user=}"
  USER="${USER#Username: }"
  if [[ -z "$USER" || "$USER" == "Not logged in"* ]]; then
    echo "✗ Not logged in. Run 'hf auth login' or export HF_TOKEN, then retry." >&2
    exit 1
  fi
  REPO="$USER/$NAME"
fi

echo "→ deploying Liferay Model to: https://huggingface.co/models/$REPO"

# Create the model repo if absent
hf repos create "$REPO" --type model --exist-ok

# Upload all files to the model repo
hf upload "$REPO" . . \
  --type model \
  --exclude "__pycache__/*" --exclude "*.pyc" --exclude "deploy_model.sh" \
  --commit-message "Upload xenτₖ Compositional Model, Liferay custom architecture"

echo "✓ live → https://huggingface.co/models/$REPO"
