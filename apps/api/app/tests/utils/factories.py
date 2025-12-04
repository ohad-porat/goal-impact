"""Factory Boy factories for creating test model instances."""

import re
from datetime import date, datetime

import factory
from factory import fuzzy

from app.models import (
    Competition,
    Event,
    GoalValueLookup,
    Match,
    Nation,
    Player,
    PlayerStats,
    Season,
    StatsCalculationMetadata,
    Team,
    TeamStats,
)


def _slugify_name(name):
    """Convert a name to a URL-friendly slug matching FBRef patterns."""
    if not name:
        return ""
    slug = name.title()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    slug = slug.strip("-")
    return slug


class NationFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Nation test data."""

    class Meta:
        model = Nation
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Test Nation {n}")
    country_code = factory.Sequence(lambda n: f"T{n:02d}")
    fbref_url = factory.LazyAttribute(
        lambda obj: f"/en/country/{obj.country_code}/{_slugify_name(obj.name)}-Football"
    )
    governing_body = "Test FA"
    clubs_url = factory.LazyAttribute(
        lambda obj: f"/en/countries/{obj.country_code}/{_slugify_name(obj.name)}-Football-Clubs"
    )


class CompetitionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Competition test data."""

    class Meta:
        model = Competition
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Test League {n}")
    gender = "M"
    competition_type = "League"
    tier = "1"
    fbref_id = factory.Sequence(lambda n: f"comp_{n:08d}")
    fbref_url = factory.LazyAttribute(
        lambda obj: f"/en/comps/{obj.fbref_id}/history/{_slugify_name(obj.name)}-Seasons"
    )
    nation = factory.SubFactory(NationFactory)


class SeasonFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Season test data."""

    class Meta:
        model = Season
        sqlalchemy_session_persistence = "commit"

    start_year = factory.Sequence(lambda n: 2020 + (n % 5))
    end_year = factory.LazyAttribute(lambda obj: obj.start_year + 1)

    @factory.lazy_attribute_sequence
    def fbref_url(self, n):
        if self.competition and self.start_year is not None and self.end_year is not None:
            slug = _slugify_name(self.competition.name)
            return (
                f"/en/comps/{self.competition.fbref_id}/{self.start_year}-{self.end_year}/"
                f"{self.start_year}-{self.end_year}-{slug}-Stats"
            )
        return f"/en/seasons/generated-{n}/"

    matches_url = factory.LazyAttribute(
        lambda obj: (
            f"/en/comps/{obj.competition.fbref_id}/{obj.start_year}-{obj.end_year}/schedule/"
            f"{obj.start_year}-{obj.end_year}-{_slugify_name(obj.competition.name)}-Scores-and-Fixtures"
        )
        if obj.competition and obj.start_year is not None and obj.end_year is not None
        else None
    )
    competition = factory.SubFactory(CompetitionFactory)


class TeamFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Team test data."""

    class Meta:
        model = Team
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Test Team {n}")
    gender = "M"
    fbref_id = factory.Sequence(lambda n: f"team_{n:08d}")
    fbref_url = factory.LazyAttribute(
        lambda obj: f"/en/squads/{obj.fbref_id}/history/{_slugify_name(obj.name)}-Stats-and-History"
    )
    nation = factory.SubFactory(NationFactory)


class PlayerFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Player test data."""

    class Meta:
        model = Player
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Test Player {n}")
    fbref_id = factory.Sequence(lambda n: f"player_{n:08d}")
    fbref_url = factory.LazyAttribute(
        lambda obj: f"/en/players/{obj.fbref_id}/{_slugify_name(obj.name)}"
    )
    nation = factory.SubFactory(NationFactory)


class MatchFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Match test data."""

    class Meta:
        model = Match
        sqlalchemy_session_persistence = "commit"

    home_team_goals = fuzzy.FuzzyInteger(0, 5)
    away_team_goals = fuzzy.FuzzyInteger(0, 5)
    date = fuzzy.FuzzyDate(start_date=date(2020, 1, 1), end_date=date(2024, 12, 31))
    fbref_id = factory.Sequence(lambda n: f"match_{n:08d}")
    fbref_url = factory.LazyAttribute(
        lambda obj: f"/en/matches/{obj.fbref_id}/{_slugify_name(obj.home_team.name)}-{_slugify_name(obj.away_team.name)}-{obj.date.strftime('%B-%d-%Y') if obj.date else 'date'}-{_slugify_name(obj.season.competition.name)}"
    )
    season = factory.SubFactory(SeasonFactory)
    home_team = factory.SubFactory(TeamFactory)
    away_team = factory.SubFactory(TeamFactory)


class EventFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Event test data."""

    class Meta:
        model = Event
        sqlalchemy_session_persistence = "commit"

    event_type = fuzzy.FuzzyChoice(["goal", "assist", "own goal", "yellow card", "red card"])
    minute = fuzzy.FuzzyInteger(1, 90)
    home_team_goals_pre_event = fuzzy.FuzzyInteger(0, 3)
    away_team_goals_pre_event = fuzzy.FuzzyInteger(0, 3)
    home_team_goals_post_event = factory.LazyAttribute(
        lambda obj: obj.home_team_goals_pre_event
        + (1 if obj.event_type in ["goal", "own goal"] else 0)
    )
    away_team_goals_post_event = factory.LazyAttribute(
        lambda obj: obj.away_team_goals_pre_event
        + (1 if obj.event_type in ["goal", "own goal"] else 0)
    )
    xg = fuzzy.FuzzyFloat(0.0, 1.0)
    post_shot_xg = fuzzy.FuzzyFloat(0.0, 1.0)
    xg_difference = factory.LazyAttribute(
        lambda obj: obj.post_shot_xg - obj.xg if obj.post_shot_xg and obj.xg else None
    )
    goal_value = fuzzy.FuzzyFloat(0.0, 1.0)
    match = factory.SubFactory(MatchFactory)
    player = factory.SubFactory(PlayerFactory)


class PlayerStatsFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating PlayerStats test data."""

    class Meta:
        model = PlayerStats
        sqlalchemy_session_persistence = "commit"

    matches_played = fuzzy.FuzzyInteger(1, 38)
    matches_started = factory.LazyAttribute(
        lambda obj: fuzzy.FuzzyInteger(0, obj.matches_played).fuzz()
    )
    total_minutes = factory.LazyAttribute(
        lambda obj: obj.matches_played * fuzzy.FuzzyInteger(60, 90).fuzz()
    )
    minutes_divided_90 = factory.LazyAttribute(
        lambda obj: round(obj.total_minutes / 90, 2) if obj.total_minutes else 0
    )
    goals_scored = fuzzy.FuzzyInteger(0, 30)
    assists = fuzzy.FuzzyInteger(0, 20)
    total_goal_assists = factory.LazyAttribute(lambda obj: obj.goals_scored + obj.assists)
    non_pk_goals = factory.LazyAttribute(
        lambda obj: max(0, obj.goals_scored - fuzzy.FuzzyInteger(0, 5).fuzz())
    )
    pk_made = fuzzy.FuzzyInteger(0, 10)
    pk_attempted = factory.LazyAttribute(lambda obj: obj.pk_made + fuzzy.FuzzyInteger(0, 3).fuzz())
    yellow_cards = fuzzy.FuzzyInteger(0, 15)
    red_cards = fuzzy.FuzzyInteger(0, 3)
    xg = fuzzy.FuzzyFloat(0.0, 25.0)
    non_pk_xg = factory.LazyAttribute(
        lambda obj: max(0.0, (obj.xg or 0.0) - fuzzy.FuzzyFloat(0.0, 5.0).fuzz())
        if obj.xg is not None
        else None
    )
    xag = fuzzy.FuzzyFloat(0.0, 20.0)
    npxg_and_xag = factory.LazyAttribute(
        lambda obj: (obj.non_pk_xg or 0.0) + (obj.xag or 0.0)
        if obj.non_pk_xg is not None and obj.xag is not None
        else None
    )
    progressive_carries = fuzzy.FuzzyInteger(0, 200)
    progressive_passes = fuzzy.FuzzyInteger(0, 300)
    progressive_passes_received = fuzzy.FuzzyInteger(0, 150)
    goal_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.goals_scored / obj.minutes_divided_90, 2)
        if obj.minutes_divided_90 > 0
        else 0
    )
    assists_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.assists / obj.minutes_divided_90, 2)
        if obj.minutes_divided_90 > 0
        else 0
    )
    total_goals_assists_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.goal_per_90 + obj.assists_per_90, 2)
    )
    non_pk_goals_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.non_pk_goals / obj.minutes_divided_90, 2)
        if obj.minutes_divided_90 > 0
        else 0
    )
    non_pk_goal_and_assists_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.non_pk_goals_per_90 + obj.assists_per_90, 2)
    )
    xg_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.xg / obj.minutes_divided_90, 2) if obj.minutes_divided_90 > 0 else 0
    )
    xag_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.xag / obj.minutes_divided_90, 2) if obj.minutes_divided_90 > 0 else 0
    )
    total_xg_xag_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.xg_per_90 + obj.xag_per_90, 2)
    )
    non_pk_xg_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.non_pk_xg / obj.minutes_divided_90, 2)
        if obj.minutes_divided_90 > 0
        else 0
    )
    npxg_and_xag_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.non_pk_xg_per_90 + obj.xag_per_90, 2)
    )
    goal_value = fuzzy.FuzzyFloat(0.0, 5.0)
    gv_avg = fuzzy.FuzzyFloat(0.0, 0.2)
    player = factory.SubFactory(PlayerFactory)
    season = factory.SubFactory(SeasonFactory)
    team = factory.SubFactory(TeamFactory)


class TeamStatsFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating TeamStats test data."""

    class Meta:
        model = TeamStats
        sqlalchemy_session_persistence = "commit"

    fbref_url = factory.LazyAttribute(
        lambda obj: f"/en/squads/{obj.team.fbref_id}/{obj.season.start_year}/{_slugify_name(obj.team.name)}-Stats"
    )
    goal_logs_url = factory.LazyAttribute(
        lambda obj: f"/en/squads/{obj.team.fbref_id}/{obj.season.start_year}/goallogs/c{obj.season.competition.fbref_id}/{_slugify_name(obj.team.name)}-Goal-Logs-{_slugify_name(obj.season.competition.name)}"
    )
    ranking = fuzzy.FuzzyInteger(1, 20)
    matches_played = fuzzy.FuzzyInteger(30, 38)
    wins = factory.LazyAttribute(lambda obj: fuzzy.FuzzyInteger(0, obj.matches_played).fuzz())
    draws = factory.LazyAttribute(
        lambda obj: fuzzy.FuzzyInteger(0, obj.matches_played - obj.wins).fuzz()
    )
    losses = factory.LazyAttribute(lambda obj: obj.matches_played - obj.wins - obj.draws)
    goals_for = fuzzy.FuzzyInteger(20, 100)
    goals_against = fuzzy.FuzzyInteger(20, 100)
    goal_difference = factory.LazyAttribute(lambda obj: obj.goals_for - obj.goals_against)
    points = factory.LazyAttribute(lambda obj: (obj.wins * 3) + (obj.draws * 1))
    points_per_match = factory.LazyAttribute(
        lambda obj: round(obj.points / obj.matches_played, 2) if obj.matches_played > 0 else 0
    )
    xg = fuzzy.FuzzyFloat(20.0, 100.0)
    xga = fuzzy.FuzzyFloat(20.0, 100.0)
    xgd = factory.LazyAttribute(lambda obj: obj.xg - obj.xga)
    xgd_per_90 = factory.LazyAttribute(
        lambda obj: round(obj.xgd / (obj.matches_played * 90) * 90, 2)
        if obj.matches_played > 0
        else 0
    )
    team = factory.SubFactory(TeamFactory)
    season = factory.SubFactory(SeasonFactory)


class GoalValueLookupFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating GoalValueLookup test data."""

    class Meta:
        model = GoalValueLookup
        sqlalchemy_session_persistence = "commit"

    minute = fuzzy.FuzzyInteger(1, 95)
    score_diff = fuzzy.FuzzyInteger(-5, 5)
    goal_value = fuzzy.FuzzyFloat(0.0, 1.0)


class StatsCalculationMetadataFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating StatsCalculationMetadata test data."""

    class Meta:
        model = StatsCalculationMetadata
        sqlalchemy_session_persistence = "commit"

    calculation_date = factory.LazyFunction(lambda: datetime.now())
    total_goals_processed = fuzzy.FuzzyInteger(1000, 10000)
    version = factory.Sequence(lambda n: f"1.{n}.0")
