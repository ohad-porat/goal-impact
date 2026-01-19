# Goal Impact

A full-stack web application for soccer data analytics featuring proprietary Goal Value (GV) metric. Built with Next.js frontend and FastAPI backend in a monorepo architecture.

## Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Data Ingestion](#data-ingestion)
- [Available Scripts](#available-scripts)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Acknowledgments](#acknowledgments)

## Tech Stack

| Layer              | Technology                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------- |
| **Frontend**       | Next.js 14 + React + TypeScript                                                             |
| **Styling**        | Tailwind CSS                                                                                |
| **Backend**        | FastAPI + Python 3.10+                                                                      |
| **Database**       | PostgreSQL                                                                                  |
| **ORM**            | SQLAlchemy 2.0 + Alembic                                                                    |
| **Data Ingestion** | Custom FBRef scraper system                                                                 |
| **Build System**   | Turborepo + Yarn Workspaces                                                                 |
| **Testing**        | Vitest + React Testing Library (Frontend), Pytest + Factory Boy (Backend), Playwright (E2E) |
| **Code Quality**   | Ruff (Python), ESLint + Prettier (TypeScript)                                               |

## Features

- **Leagues**: Browse competitions, view league tables, and explore season-by-season standings
- **Clubs**: Team statistics, season rosters, and goal logs with player contributions
- **Players**: Career statistics, season-by-season performance, and detailed goal logs
- **Nations**: National team data with top players and clubs by country
- **Leaders**: Career totals and seasonal leaderboards with league filtering
- **Search**: Global search across players, clubs, competitions, and nations
- **Goal Value Analytics**: Proprietary metric for evaluating goal significance and impact

## Prerequisites

- **Node.js** 18+ and **Yarn** 1.22+
- **Python** 3.10+ with pip
- **PostgreSQL** database server
- **Git** for version control

## Quick Start

### 1. Install Dependencies

```bash
yarn install
yarn db:setup
```

### 2. Create Database

Create a PostgreSQL database for the application.

### 3. Environment Configuration

Create environment files for both applications:

**`apps/api/.env.local`** - Required variables:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/goal_impact
ALLOWED_HOSTS=["http://localhost:3000"]
```

**`apps/web/.env.local`** - Required variables:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Adjust these values according to your local setup.

### 4. Run Migrations

```bash
yarn db:migrate
```

### 5. Start Development Servers

```bash
yarn dev
```

This will start:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## Data Ingestion

The platform includes a comprehensive FBRef scraper system with multiple operational modes for collecting soccer data.

### Scraper Modes

- **Initial Mode**: Full data scrape for all supported leagues and seasons. Scrapes nations, competitions, seasons, teams, team stats, players, matches, and events.
- **Daily Mode**: Incremental updates for recent matches and events. Updates team and player statistics for affected seasons.
- **Seasonal Mode**: Handles new seasons, URL changes, and season transitions. Verifies and updates season data.

### Usage

```bash
cd apps/api
source venv/bin/activate

# Full initial scrape (run this first for new installations)
python -m app.fbref_scraper.main_scraper --mode initial

# Daily updates (last N days)
python -m app.fbref_scraper.main_scraper --mode daily --days 7

# Seasonal updates (handle new seasons)
python -m app.fbref_scraper.main_scraper --mode seasonal

# Resume from interruption
python -m app.fbref_scraper.main_scraper --mode initial --resume

# Custom date range
python -m app.fbref_scraper.main_scraper --mode daily --from-date 2024-01-01 --to-date 2024-01-31

# Filter by nations
python -m app.fbref_scraper.main_scraper --mode initial --nations "England,Spain,Germany"

# Year range filtering
python -m app.fbref_scraper.main_scraper --mode initial --from-year 2020 --to-year 2023

# Continue on errors
python -m app.fbref_scraper.main_scraper --mode initial --continue-on-error
```

## Available Scripts

### Root Level

```bash
yarn dev          # Start all development servers
yarn build        # Build all applications
yarn lint         # Lint all applications
yarn type-check   # Type check TypeScript code
yarn format       # Format code with Prettier
yarn clean        # Clean build artifacts
yarn db:setup     # Create Python virtual environment and install dependencies
yarn db:migrate   # Run database migrations
```

## Testing

The project includes comprehensive test coverage across multiple layers:

### Test Structure

**Backend Tests:**

- **Unit Tests**: Models, services, schemas, and goal value core logic
- **Integration Tests**: API route endpoints
- **Scraper Tests**: FBRef scraper system components

**Frontend Tests:**

- **Component Tests**: React components with user interaction testing
- **Hook Tests**: Custom React hooks and data fetching logic
- **Utility Tests**: Helper functions and API client utilities
- **E2E Tests**: End-to-end browser tests covering navigation, pages, search, mobile responsiveness, and error handling

### Running Tests

**Backend Tests (Python):**

```bash
cd apps/api
source venv/bin/activate

# Run all tests
pytest

# Run specific test suites
pytest app/tests/unit/              # Unit tests
pytest app/tests/integration/       # Integration tests
pytest app/fbref_scraper/tests/     # Scraper tests

# Run specific test file
pytest app/tests/unit/services/test_players.py
pytest app/tests/integration/test_routes_players.py
pytest app/fbref_scraper/tests/unit/test_config.py

# Run with coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v
```

**Frontend Tests (TypeScript/React):**

```bash
cd apps/web

# Run all tests
yarn test

# Run tests in watch mode
yarn test:watch

# Run tests with UI
yarn test:ui

# Run tests with coverage
yarn test:coverage

# Run specific test file
yarn test SearchBar.test.tsx
```

**E2E Tests (Playwright):**

E2E tests require the backend API to be running. The easiest way to run them locally is using the automated script:

```bash
cd apps/web
./scripts/run_e2e_local.sh
```

This script automatically:

- Sets up a test database (SQLite)
- Runs migrations
- Seeds test data
- Starts the API server
- Runs the E2E tests
- Cleans up afterward

**Alternative: Manual Setup**

If you want to run tests against your own running backend:

```bash
# 1. Ensure backend API is running on http://localhost:8000
# 2. Ensure frontend is running on http://localhost:3000 (or built and started)

cd apps/web

# Run all E2E tests
yarn test:e2e

# Run E2E tests with UI
yarn test:e2e:ui

# Run E2E tests in debug mode
yarn test:e2e:debug

# Run E2E tests in headed mode (visible browser)
yarn test:e2e:headed

# Run specific E2E test file
yarn test:e2e e2e/home.spec.ts
```

### CI/CD

The project uses GitHub Actions for continuous integration, running:

- **Backend**: Unit tests for models, services, and schemas; Integration tests for API routes; Scraper tests
- **Frontend**: Component tests, hook tests, and utility tests using Vitest
- **E2E**: Browser-based end-to-end tests using Playwright (Chromium in CI, all browsers locally)
- **Code Quality**: Linting and formatting checks (Ruff for Python, ESLint for TypeScript)

## API Endpoints

The API provides the following endpoints:

### Core Endpoints

- `GET /` - API information and version
- `GET /health` - Health check endpoint

### Leagues

- `GET /api/v1/leagues` - List all leagues with season ranges
- `GET /api/v1/leagues/seasons` - Get all unique seasons across all leagues
- `GET /api/v1/leagues/{id}/seasons` - Get all seasons for a specific league
- `GET /api/v1/leagues/{id}/table/{season_id}` - Get league table for a specific season

### Clubs

- `GET /api/v1/clubs` - List top clubs grouped by nation
- `GET /api/v1/clubs/{id}` - Get club details with season statistics
- `GET /api/v1/clubs/{id}/seasons/{season_id}` - Get team squad with player statistics for a season
- `GET /api/v1/clubs/{id}/seasons/{season_id}/goals` - Get goal log for a team in a specific season

### Players

- `GET /api/v1/players/{id}` - Get player details with statistics across all seasons
- `GET /api/v1/players/{id}/goals` - Get player career goal log

### Nations

- `GET /api/v1/nations` - List all nations with player counts
- `GET /api/v1/nations/{id}` - Get nation details with top players and clubs

### Leaders

- `GET /api/v1/leaders/career-totals` - Career goal value leaderboards
  - Query params: `limit` (1-100, default: 50), `league_id` (optional)
- `GET /api/v1/leaders/by-season` - Seasonal goal value leaderboards
  - Query params: `season_id` (required), `limit` (1-100, default: 50), `league_id` (optional)

### Search & Home

- `GET /api/v1/search` - Global search across players, clubs, competitions, and nations
  - Query params: `q` (required, min length: 1)
- `GET /api/v1/home/recent-goals` - Recent high-impact goals from the past week
  - Query params: `league_id` (optional)

## Development

### Code Style

- **Python**: Follow PEP 8 style guidelines, enforced with Ruff
- **TypeScript/JavaScript**: ESLint and Prettier configurations

### Code Quality Tools

- **Ruff**: Fast Python linter and formatter (replaces Black, isort, flake8)
- **ESLint**: TypeScript/JavaScript linting
- **Prettier**: Code formatting for TypeScript, JavaScript, and Markdown
- **Pytest**: Testing framework with coverage reporting for Python
- **Vitest**: Fast unit test framework for TypeScript/React with coverage reporting
- **Playwright**: End-to-end browser testing framework for full user flow validation
- **TypeScript**: Static type checking for frontend code

## Acknowledgments

- [FBref](https://fbref.com/) for comprehensive soccer statistics
