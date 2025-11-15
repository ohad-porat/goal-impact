#!/bin/bash
# Restore a dump file (stable or prod) to local database
# Usage: ./scripts/restore_dump_to_local.sh <dump_file> [local_database_url]

if [ -z "$1" ]; then
  echo "Usage: ./scripts/restore_dump_to_local.sh <dump_file> [local_database_url]"
  echo ""
  echo "Examples:"
  echo "  ./scripts/restore_dump_to_local.sh goal_impact_stable_24_25.dump"
  echo "  ./scripts/restore_dump_to_local.sh goal_impact_prod_20250115_120000.dump"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_DIR="$SCRIPT_DIR/../db"

DUMP_FILE="$1"
if [[ "$DUMP_FILE" != /* ]]; then
  DUMP_FILE="$DB_DIR/$DUMP_FILE"
fi

if [ -f .env.local ]; then
  export $(cat .env.local | grep -v '^#' | xargs)
fi

LOCAL_DB_URL="${2:-${DATABASE_URL}}"

if [ -z "$LOCAL_DB_URL" ]; then
  echo "Error: DATABASE_URL not set. Provide it as second argument or set in .env.local"
  exit 1
fi

if [ ! -f "$DUMP_FILE" ]; then
  echo "Error: Dump file not found: $DUMP_FILE"
  exit 1
fi

echo "WARNING: This will replace your local database!"
echo "Restoring $DUMP_FILE to local database..."
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Restore cancelled."
  exit 0
fi

pg_restore -d "$LOCAL_DB_URL" --clean --if-exists --no-owner --no-acl "$DUMP_FILE"

if [ $? -eq 0 ]; then
  echo "Restore completed successfully!"
else
  echo "Restore failed!"
  exit 1
fi
