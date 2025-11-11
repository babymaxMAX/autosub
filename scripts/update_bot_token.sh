#!/bin/bash

set -euo pipefail

# Simple helper to update BOT_TOKEN in project .env
# Usage:
#   bash scripts/update_bot_token.sh NEW_TOKEN [--restart]

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_DIR/.env"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 NEW_TOKEN [--restart]" >&2
  exit 1
fi

NEW_TOKEN="$1"
DO_RESTART="false"
if [[ ${2-} == "--restart" ]]; then
  DO_RESTART="true"
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: $ENV_FILE not found" >&2
  exit 1
fi

# Backup current .env
TS="$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$ENV_FILE.bak.$TS"

# Update or insert BOT_TOKEN (macOS-compatible sed -i '')
if grep -q '^BOT_TOKEN=' "$ENV_FILE"; then
  sed -i '' "s|^BOT_TOKEN=.*|BOT_TOKEN=$NEW_TOKEN|" "$ENV_FILE"
else
  printf "\nBOT_TOKEN=%s\n" "$NEW_TOKEN" >> "$ENV_FILE"
fi

echo "BOT_TOKEN updated in $ENV_FILE"

if [[ "$DO_RESTART" == "true" ]]; then
  echo "Restarting bot container..."
  (cd "$PROJECT_DIR" && docker compose up -d --build bot)
  echo "Bot restarted. Use: docker compose logs -f bot"
fi


