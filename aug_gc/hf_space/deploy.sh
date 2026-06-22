#!/usr/bin/env bash
# One-command deploy of the aug_gc Gradio Space to HuggingFace.
#
#   ./deploy.sh                       # → space named "aug_gc" under your HF account
#   ./deploy.sh my-space-name         # → custom space name
#   SPACE=org/aug_gc ./deploy.sh      # → explicit owner/repo (e.g. an org)
#
# Auth: run `hf auth login` once, or export HF_TOKEN.
# Idempotent: creates the Space on first run, updates files on every run.
set -euo pipefail

cd "$(dirname "$0")"

# ── Ensure the modern HF CLI (`hf`) is present ───────────────
# `hf` replaces the deprecated `huggingface-cli`.
if ! command -v hf >/dev/null 2>&1; then
  echo "→ installing the hf CLI…"
  curl -LsSf https://hf.co/cli/install.sh | bash -s
  export PATH="$HOME/.local/bin:$PATH"
fi

# ── Resolve the target repo id (owner/space) ─────────────────
if [[ -n "${SPACE:-}" ]]; then
  REPO="$SPACE"
else
  NAME="${1:-aug_gc}"
  USER="$(hf auth whoami 2>/dev/null | head -1 || true)"
  if [[ -z "$USER" || "$USER" == "Not logged in"* ]]; then
    echo "✗ Not logged in. Run 'hf auth login' or export HF_TOKEN, then retry." >&2
    exit 1
  fi
  REPO="$USER/$NAME"
fi

echo "→ deploying aug_gc Space to: https://huggingface.co/spaces/$REPO"

# ── Create the Space if absent (Gradio SDK); --exist-ok is idempotent ──
hf repos create "$REPO" --type space --space-sdk gradio --exist-ok

# ── Upload everything except local cruft, in one commit ──────
hf upload "$REPO" . . \
  --type space \
  --exclude "__pycache__/*" --exclude "*.pyc" --exclude "*.png" \
  --exclude ".venv/*" --exclude "temporal_manuscript.json" \
  --commit-message "Deploy aug_gc — temporal composition Space"

echo "✓ live → https://huggingface.co/spaces/$REPO"
