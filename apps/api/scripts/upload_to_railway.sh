#!/bin/bash
# Upload a dump file (stable or prod) to Railway database
# Usage: ./scripts/upload_to_railway.sh <dump_file> <railway_database_url>

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: ./scripts/upload_to_railway.sh <dump_file> <railway_database_url>"
  echo ""
  echo "Get railway_database_url from Railway dashboard:"
  echo "1. Go to Postgres service → Variables tab"
  echo "2. Copy the DATABASE_PUBLIC_URL"
  echo ""
  echo "Examples:"
  echo "  ./scripts/upload_to_railway.sh goal_impact_stable_24_25.dump \$RAILWAY_DB_URL"
  echo "  ./scripts/upload_to_railway.sh goal_impact_prod_20250115_120000.dump \$RAILWAY_DB_URL"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_DIR="$SCRIPT_DIR/../db"

DUMP_FILE="$1"
if [[ "$DUMP_FILE" != /* ]]; then
  DUMP_FILE="$DB_DIR/$DUMP_FILE"
fi

RAILWAY_DB_URL="$2"

if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: Dump file not found: $DUMP_FILE"
  exit 1
fi

echo "WARNING: This will replace the Railway database!"
echo "Uploading $DUMP_FILE to Railway database..."
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Upload cancelled."
  exit 0
fi

pg_restore -d "$RAILWAY_DB_URL" --clean --if-exists --no-owner --no-acl "$DUMP_FILE"

if [ $? -eq 0 ]; then
  echo "Upload to Railway completed successfully!"
else
  echo "Upload failed!"
  exit 1
fi
