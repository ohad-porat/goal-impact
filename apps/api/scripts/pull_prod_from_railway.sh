#!/bin/bash
# Pull latest production data from Railway and create local prod dump
# Usage: ./scripts/pull_prod_from_railway.sh <railway_database_url> [output_file]

if [ -z "$1" ]; then
  echo "Usage: ./scripts/pull_prod_from_railway.sh <railway_database_url> [output_file]"
  echo ""
  echo "Get railway_database_url from Railway dashboard:"
  echo "1. Go to Postgres service → Variables tab"
  echo "2. Copy the DATABASE_PUBLIC_URL"
  echo ""
  echo "If output_file is not provided, creates timestamped file: goal_impact_prod_YYYYMMDD_HHMMSS.dump"
  echo "Note: This creates a NEW file each time (does not overwrite existing prod dumps)"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_DIR="$SCRIPT_DIR/../db"

RAILWAY_DB_URL="$1"
OUTPUT_FILE="${2:-goal_impact_prod_$(date +%Y%m%d_%H%M%S).dump}"

if [[ "$OUTPUT_FILE" != /* ]]; then
  mkdir -p "$DB_DIR"
  OUTPUT_FILE="$DB_DIR/$OUTPUT_FILE"
fi

if [ -n "$2" ] && [ -f "$OUTPUT_FILE" ]; then
  echo "WARNING: File $OUTPUT_FILE already exists!"
  read -p "Overwrite? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
  fi
fi

echo "Pulling latest production data from Railway..."
echo "Creating dump: $OUTPUT_FILE"

pg_dump "$RAILWAY_DB_URL" -F c -f "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
  echo "Production dump created successfully: $OUTPUT_FILE"
  echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
  echo ""
  echo "To restore to local: ./scripts/restore_dump_to_local.sh $OUTPUT_FILE"
  echo "To upload to Railway: ./scripts/upload_to_railway.sh $OUTPUT_FILE \$RAILWAY_DB_URL"
else
  echo "Backup failed!"
  exit 1
fi
