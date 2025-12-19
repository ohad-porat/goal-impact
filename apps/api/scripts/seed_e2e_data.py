#!/usr/bin/env python3
"""Seed script for e2e test database.

Creates minimal test data required for e2e tests to pass.
"""

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Competition, Event, Match, Nation, Player, PlayerStats, Season, Team, TeamStats
from app.tests.utils.factories import (
    CompetitionFactory,
    EventFactory,
    MatchFactory,
    NationFactory,
    PlayerFactory,
    PlayerStatsFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)
from app.tests.utils.helpers import create_goal_event


def seed_e2e_database(db_url: str):
    """Seed the database with minimal test data for e2e tests."""
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    factory_classes = [
        NationFactory,
        CompetitionFactory,
        SeasonFactory,
        TeamFactory,
        PlayerFactory,
        MatchFactory,
        EventFactory,
        PlayerStatsFactory,
        TeamStatsFactory,
    ]

    for factory_class in factory_classes:
        factory_class._meta.sqlalchemy_session = session

    try:
        nation1 = NationFactory(name="England", country_code="ENG")
        nation2 = NationFactory(name="Spain", country_code="ESP")
        session.commit()

        comp1 = CompetitionFactory(name="Premier League", nation=nation1, tier="1st")
        comp2 = CompetitionFactory(name="La Liga", nation=nation2, tier="1st")
        session.commit()

        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        season3 = SeasonFactory(competition=comp1, start_year=2022, end_year=2023)
        session.commit()

        team1 = TeamFactory(name="Arsenal", nation=nation1)
        team2 = TeamFactory(name="Manchester City", nation=nation1)
        team3 = TeamFactory(name="Real Madrid", nation=nation2)
        team4 = TeamFactory(name="Barcelona", nation=nation2)
        session.commit()

        player1 = PlayerFactory(name="Test Player 1", nation=nation1)
        player2 = PlayerFactory(name="Test Player 2", nation=nation2)
        session.commit()

        recent_date = date.today() - timedelta(days=2)
        match1 = MatchFactory(
            season=season1,
            home_team=team1,
            away_team=team2,
            date=recent_date,
            home_team_goals=2,
            away_team_goals=1,
        )
        match2 = MatchFactory(
            season=season2,
            home_team=team3,
            away_team=team4,
            date=recent_date,
            home_team_goals=1,
            away_team_goals=0,
        )
        match3 = MatchFactory(
            season=season3,
            home_team=team1,
            away_team=team2,
            date=recent_date - timedelta(days=365),
            home_team_goals=1,
            away_team_goals=1,
        )
        session.commit()

        create_goal_event(
            match1,
            player1,
            minute=45,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            goal_value=0.65,
        )
        create_goal_event(
            match1,
            player1,
            minute=89,
            home_pre=1,
            home_post=2,
            away_pre=0,
            away_post=0,
            goal_value=0.85,
        )
        create_goal_event(
            match2,
            player2,
            minute=60,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            goal_value=0.70,
        )
        create_goal_event(
            match3,
            player1,
            minute=30,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            goal_value=0.50,
        )
        session.commit()

        PlayerStatsFactory(
            player=player1,
            season=season1,
            team=team1,
            goal_value=1.50,
            goals_scored=2,
        )
        PlayerStatsFactory(
            player=player2,
            season=season2,
            team=team3,
            goal_value=0.70,
            goals_scored=1,
        )
        PlayerStatsFactory(
            player=player1,
            season=season3,
            team=team1,
            goal_value=0.50,
            goals_scored=1,
        )
        session.commit()

        TeamStatsFactory(
            team=team1,
            season=season1,
            ranking=1,
            matches_played=38,
            wins=28,
            draws=5,
            losses=5,
        )
        TeamStatsFactory(
            team=team2,
            season=season1,
            ranking=2,
            matches_played=38,
            wins=26,
            draws=7,
            losses=5,
        )
        TeamStatsFactory(
            team=team3,
            season=season2,
            ranking=1,
            matches_played=38,
            wins=29,
            draws=4,
            losses=5,
        )
        TeamStatsFactory(
            team=team4,
            season=season2,
            ranking=2,
            matches_played=38,
            wins=27,
            draws=6,
            losses=5,
        )
        TeamStatsFactory(
            team=team1,
            season=season3,
            ranking=1,
            matches_played=38,
            wins=25,
            draws=8,
            losses=5,
        )
        TeamStatsFactory(
            team=team2,
            season=season3,
            ranking=2,
            matches_played=38,
            wins=24,
            draws=7,
            losses=7,
        )
        session.commit()

        print("\n✅ E2E test data seeded successfully!")
        print(f"   - Created {session.query(Nation).count()} nations")
        print(f"   - Created {session.query(Competition).count()} competitions")
        print(f"   - Created {session.query(Season).count()} seasons")
        print(f"   - Created {session.query(Team).count()} teams")
        print(f"   - Created {session.query(Player).count()} players")
        print(f"   - Created {session.query(Match).count()} matches")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL environment variable is required")
        sys.exit(1)

    seed_e2e_database(db_url)
