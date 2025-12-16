#!/bin/bash
# Run e2e tests locally with test database (like CI)
# Usage: ./scripts/run_e2e_local.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WEB_DIR="$SCRIPT_DIR/.."
API_DIR="$SCRIPT_DIR/../../api"
TEST_DB_DIR="/tmp/e2e_test"
TEST_DB_FILE="$TEST_DB_DIR/test.db"
TEST_DB_URL="sqlite:///$TEST_DB_FILE"

cd "$API_DIR"

if [ ! -d "venv" ]; then
  echo "Error: API venv not found. Please run 'yarn db:setup' first"
  exit 1
fi

echo "🔧 Setting up test database..."
source venv/bin/activate
export DATABASE_URL="$TEST_DB_URL"
export ALLOWED_HOSTS='["*"]'

rm -rf "$TEST_DB_DIR"
mkdir -p "$TEST_DB_DIR"

echo "📦 Running migrations..."
alembic upgrade head

echo "🌱 Seeding database..."
python scripts/seed_e2e_data.py

echo "🚀 Starting API server..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/api_server.log 2>&1 &
API_PID=$!
echo "API server PID: $API_PID"

echo "⏳ Waiting for API server to be ready..."
for i in {1..30}; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API server is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ API server failed to start"
    cat /tmp/api_server.log
    kill $API_PID 2>/dev/null || true
    exit 1
  fi
  echo "   Waiting... ($i/30)"
  sleep 1
done

cd "$WEB_DIR"

echo "🧪 Running e2e tests..."
export NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
export PLAYWRIGHT_TEST_BASE_URL=http://localhost:3000
yarn test:e2e "$@"
TEST_EXIT_CODE=$?

echo "🛑 Stopping API server..."
kill $API_PID 2>/dev/null || true

if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "✅ All tests passed!"
else
  echo "❌ Tests failed with exit code $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE

