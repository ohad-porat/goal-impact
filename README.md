# Goal Impact

A full-stack web application for soccer data analytics featuring proprietary **Goal Value (GV) metric. Built with Next.js frontend and FastAPI backend in a monorepo architecture.

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14 + React + TypeScript | Modern web UI with App Router |
| **Styling** | Tailwind CSS + ShadCN UI | Responsive design system |
| **Backend** | FastAPI + Python 3.11+ | REST API with async support |
| **Database** | SQLite + TimescaleDB | Structured data storage |
| **ORM** | SQLAlchemy + Alembic | Database management |
| **Data Ingestion** | Custom FBRef scraper system | Multi-mode data scraping with CLI |
| **Build System** | Turborepo + Yarn Workspaces | Monorepo orchestration |

## Prerequisites

- **Node.js** 18+ and **Yarn** 1.22+
- **Python** 3.11+ with pip
- **SQLite** (included with Python)
- **Git** for version control

## Quick Start

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd goal-impact
yarn install
yarn db:setup
```

### 2. Database Setup

```bash
yarn db:migrate
```

### 3. Environment Configuration

```bash
cp apps/web/env.local.example apps/web/.env.local
```

### 4. Start Development Servers

```bash
yarn dev
```

## Data Ingestion

The platform includes a comprehensive FBRef scraper system with multiple operational modes for collecting soccer data:

```bash
cd apps/api
source venv/bin/activate

# Full initial scrape
python -m app.fbref_scraper.main_scraper --mode initial

# Daily updates
python -m app.fbref_scraper.main_scraper --mode daily --days 7

# Seasonal updates
python -m app.fbref_scraper.main_scraper --mode seasonal

# Resume from interruption
python -m app.fbref_scraper.main_scraper --mode initial --resume

# Or use yarn script
yarn ingest
```

### Scraper Modes

- **Initial Mode**: Full data scrape for all supported leagues and seasons
- **Daily Mode**: Incremental updates for recent matches and events
- **Seasonal Mode**: Handle new seasons and URL changes
- **Resume Support**: Continue from interruption points
- **Progress Tracking**: Built-in progress management and error handling

## Available Scripts

### Root Level (Turborepo)

```bash
yarn dev
yarn build
yarn lint
yarn type-check
yarn clean
yarn format
```

### Database & Data

```bash
yarn db:setup
yarn db:migrate
yarn ingest
```

## Testing

The project includes a comprehensive test suite for the FBRef scraper system:

```bash
cd apps/api
source venv/bin/activate
pytest

pytest app/fbref_scraper/tests/unit/test_config.py
pytest app/fbref_scraper/tests/unit/test_base_scraper.py

pytest --cov=app.fbref_scraper
pytest -v
```

## 🙏 Acknowledgments

- [FBref](https://fbref.com/) for comprehensive soccer statistics
