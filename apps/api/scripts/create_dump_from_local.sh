#!/bin/bash
# Create a dump file from local database
# Usage: ./scripts/create_dump_from_local.sh <output_file> [local_database_url]

if [ -z "$1" ]; then
  echo "Usage: ./scripts/create_dump_from_local.sh <output_file> [local_database_url]"
  echo ""
  echo "Examples:"
  echo "  ./scripts/create_dump_from_local.sh goal_impact_prod_20250115_120000.dump"
  echo "  ./scripts/create_dump_from_local.sh goal_impact_stable_24_25.dump"
  echo ""
  echo "If local_database_url is not provided, uses DATABASE_URL from .env.local"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_DIR="$SCRIPT_DIR/../db"

OUTPUT_FILE="$1"
if [[ "$OUTPUT_FILE" != /* ]]; then
  mkdir -p "$DB_DIR"
  OUTPUT_FILE="$DB_DIR/$OUTPUT_FILE"
fi

if [ -f .env.local ]; then
  export $(cat .env.local | grep -v '^#' | xargs)
fi

LOCAL_DB_URL="${2:-${DATABASE_URL}}"

if [ -z "$LOCAL_DB_URL" ]; then
  echo "Error: DATABASE_URL not set. Provide it as second argument or set in .env.local"
  exit 1
fi

if [ -f "$OUTPUT_FILE" ]; then
  echo "WARNING: File $OUTPUT_FILE already exists!"
  read -p "Overwrite? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
  fi
fi

echo "Creating dump from local database..."
echo "Output file: $OUTPUT_FILE"

pg_dump "$LOCAL_DB_URL" -F c -f "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
  echo "Dump created successfully: $OUTPUT_FILE"
  echo "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
  echo ""
  echo "To restore to local: ./scripts/restore_dump_to_local.sh $OUTPUT_FILE"
  echo "To upload to Railway: ./scripts/upload_to_railway.sh $OUTPUT_FILE \$RAILWAY_DB_URL"
else
  echo "Dump failed!"
  exit 1
fi
