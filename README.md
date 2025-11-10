# Goal Impact

A full-stack web application for soccer data analytics featuring proprietary Goal Value (GV) metric. Built with Next.js frontend and FastAPI backend in a monorepo architecture.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14 + React + TypeScript |
| **Styling** | Tailwind CSS |
| **Backend** | FastAPI + Python 3.9+ |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 + Alembic |
| **Data Ingestion** | Custom FBRef scraper system |
| **Build System** | Turborepo + Yarn Workspaces |
| **Testing** | Pytest + Factory Boy |

## Features

- **Leagues, Clubs, Players & Nations**: Browse statistics, standings, and performance metrics
- **Leaders**: Career totals and seasonal leaderboards
- **Search**: Global search across all entities
- **Goal Value Analytics**: Proprietary metric for evaluating goal significance

## Prerequisites

- **Node.js** 18+ and **Yarn** 1.22+
- **Python** 3.9+ with pip
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

Copy the example environment files and configure them:

```bash
cp apps/api/.env.example apps/api/.env.local
cp apps/web/.env.example apps/web/.env.local
```

Edit the `.env.local` files with your database connection string and other required values.

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
yarn db:setup     # Create Python virtual environment and install dependencies
yarn db:migrate   # Run database migrations
```

## Testing

The project currently includes test coverage for the FBRef scraper system:

```bash
cd apps/api
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest app/fbref_scraper/tests/unit/test_config.py
pytest app/fbref_scraper/tests/unit/test_base_scraper.py

# Run with coverage
pytest --cov=app.fbref_scraper

# Verbose output
pytest -v
```

## API Endpoints

The API provides the following main endpoints:

- `GET /api/v1/leagues` - List all leagues
- `GET /api/v1/leagues/{id}` - League details
- `GET /api/v1/clubs` - List all clubs
- `GET /api/v1/clubs/{id}` - Club details
- `GET /api/v1/players/{id}` - Player details
- `GET /api/v1/nations` - List all nations
- `GET /api/v1/nations/{id}` - Nation details
- `GET /api/v1/leaders/career-totals` - Career leaderboards
- `GET /api/v1/leaders/by-season` - Seasonal leaderboards
- `GET /api/v1/search` - Global search
- `GET /api/v1/home/recent-goals` - Recent high-impact goals

## Development

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **TypeScript/JavaScript**: ESLint and Prettier configurations

## Acknowledgments

- [FBref](https://fbref.com/) for comprehensive soccer statistics
