#!/bin/bash
# Script to run database migrations on Railway
# Usage: ./scripts/run_railway_migrations.sh <DATABASE_PUBLIC_URL>

if [ -z "$1" ]; then
  echo "Usage: ./scripts/run_railway_migrations.sh <DATABASE_PUBLIC_URL>"
  echo ""
  echo "Get DATABASE_PUBLIC_URL from Railway dashboard:"
  echo "1. Go to Postgres service → Variables tab"
  echo "2. Copy the DATABASE_PUBLIC_URL"
  exit 1
fi

export DATABASE_URL="$1"
cd "$(dirname "$0")/.."  # Go to apps/api directory
source venv/bin/activate
alembic upgrade head

