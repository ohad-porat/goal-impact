"""Factory Boy factories for creating test data."""

import factory
from factory import fuzzy
from datetime import date
from models import (
    Nation, Competition, Season, Team, Player, Match, Event,
    PlayerStats, TeamStats
)


class NationFactory(factory.Factory):
    """Factory for creating Nation test data."""
    class Meta:
        model = Nation
    
    name = factory.Sequence(lambda n: f"Test Nation {n}")
    country_code = factory.Sequence(lambda n: f"T{n:02d}")
    fbref_url = factory.LazyAttribute(lambda obj: f"/en/countries/{obj.country_code}/")
    governing_body = "Test FA"
    clubs_url = factory.LazyAttribute(lambda obj: f"/en/countries/{obj.country_code}/clubs/")


class CompetitionFactory(factory.Factory):
    """Factory for creating Competition test data."""
    class Meta:
        model = Competition
    
    name = factory.Sequence(lambda n: f"Test League {n}")
    gender = "M"
    competition_type = "League"
    tier = "1"
    fbref_id = factory.Sequence(lambda n: f"comp_{n:08d}")
    fbref_url = factory.LazyAttribute(lambda obj: f"/en/competitions/{obj.fbref_id}/")
    nation = factory.SubFactory(NationFactory)


class SeasonFactory(factory.Factory):
    """Factory for creating Season test data."""
    class Meta:
        model = Season
    
    start_year = factory.Sequence(lambda n: 2020 + n)
    end_year = factory.LazyAttribute(lambda obj: obj.start_year + 1)
    fbref_url = factory.LazyAttribute(lambda obj: f"/en/seasons/{obj.start_year}-{obj.end_year}/")
    matches_url = factory.LazyAttribute(lambda obj: f"/en/seasons/{obj.start_year}-{obj.end_year}/matches/")
    competition = factory.SubFactory(CompetitionFactory)


class TeamFactory(factory.Factory):
    """Factory for creating Team test data."""
    class Meta:
        model = Team
    
    name = factory.Sequence(lambda n: f"Test Team {n}")
    gender = "M"
    fbref_id = factory.Sequence(lambda n: f"team_{n:08d}")
    fbref_url = factory.LazyAttribute(lambda obj: f"/en/squads/{obj.fbref_id}/")
    nation = factory.SubFactory(NationFactory)


class PlayerFactory(factory.Factory):
    """Factory for creating Player test data."""
    class Meta:
        model = Player
    
    name = factory.Sequence(lambda n: f"Test Player {n}")
    fbref_id = factory.Sequence(lambda n: f"player_{n:08d}")
    fbref_url = factory.LazyAttribute(lambda obj: f"/en/players/{obj.fbref_id}/")
    nation = factory.SubFactory(NationFactory)


class MatchFactory(factory.Factory):
    """Factory for creating Match test data."""
    class Meta:
        model = Match
    
    home_team_goals = fuzzy.FuzzyInteger(0, 5)
    away_team_goals = fuzzy.FuzzyInteger(0, 5)
    date = fuzzy.FuzzyDate(start_date=date(2020, 1, 1), end_date=date(2024, 12, 31))
    fbref_id = factory.Sequence(lambda n: f"match_{n:08d}")
    fbref_url = factory.LazyAttribute(lambda obj: f"/en/matches/{obj.fbref_id}/")
    season = factory.SubFactory(SeasonFactory)
    home_team = factory.SubFactory(TeamFactory)
    away_team = factory.SubFactory(TeamFactory)


class EventFactory(factory.Factory):
    """Factory for creating Event test data."""
    class Meta:
        model = Event
    
    event_type = fuzzy.FuzzyChoice(['goal', 'assist', 'own goal'])
    minute = fuzzy.FuzzyInteger(1, 90)
    home_team_goals_pre_event = fuzzy.FuzzyInteger(0, 3)
    away_team_goals_pre_event = fuzzy.FuzzyInteger(0, 3)
    home_team_goals_post_event = factory.LazyAttribute(lambda obj: obj.home_team_goals_pre_event + (1 if obj.event_type in ['goal', 'own goal'] else 0))
    away_team_goals_post_event = factory.LazyAttribute(lambda obj: obj.away_team_goals_pre_event + (1 if obj.event_type in ['goal', 'own goal'] else 0))
    xg = fuzzy.FuzzyFloat(0.0, 1.0)
    post_shot_xg = fuzzy.FuzzyFloat(0.0, 1.0)
    xg_difference = factory.LazyAttribute(lambda obj: obj.post_shot_xg - obj.xg if obj.post_shot_xg and obj.xg else None)
    points_added = fuzzy.FuzzyFloat(-1.0, 1.0)
    goal_value = fuzzy.FuzzyFloat(0.0, 1.0)
    match = factory.SubFactory(MatchFactory)
    player = factory.SubFactory(PlayerFactory)


class PlayerStatsFactory(factory.Factory):
    """Factory for creating PlayerStats test data."""
    class Meta:
        model = PlayerStats
    
    matches_played = fuzzy.FuzzyInteger(1, 38)
    matches_started = factory.LazyAttribute(lambda obj: fuzzy.FuzzyInteger(0, obj.matches_played).fuzz())
    total_minutes = factory.LazyAttribute(lambda obj: obj.matches_played * fuzzy.FuzzyInteger(60, 90).fuzz())
    minutes_divided_90 = factory.LazyAttribute(lambda obj: obj.total_minutes / 90 if obj.total_minutes else 0)
    goals_scored = fuzzy.FuzzyInteger(0, 30)
    assists = fuzzy.FuzzyInteger(0, 20)
    total_goal_assists = factory.LazyAttribute(lambda obj: obj.goals_scored + obj.assists)
    non_pk_goals = factory.LazyAttribute(lambda obj: max(0, obj.goals_scored - fuzzy.FuzzyInteger(0, 5).fuzz()))
    pk_made = fuzzy.FuzzyInteger(0, 10)
    pk_attempted = factory.LazyAttribute(lambda obj: obj.pk_made + fuzzy.FuzzyInteger(0, 3).fuzz())
    yellow_cards = fuzzy.FuzzyInteger(0, 15)
    red_cards = fuzzy.FuzzyInteger(0, 3)
    xg = fuzzy.FuzzyFloat(0.0, 25.0)
    non_pk_xg = factory.LazyAttribute(lambda obj: max(0, obj.xg - fuzzy.FuzzyFloat(0.0, 5.0).fuzz()))
    xag = fuzzy.FuzzyFloat(0.0, 20.0)
    npxg_and_xag = factory.LazyAttribute(lambda obj: obj.non_pk_xg + obj.xag)
    progressive_carries = fuzzy.FuzzyInteger(0, 200)
    progressive_passes = fuzzy.FuzzyInteger(0, 300)
    progressive_passes_received = fuzzy.FuzzyInteger(0, 150)
    goal_per_90 = factory.LazyAttribute(lambda obj: (obj.goals_scored / obj.minutes_divided_90) if obj.minutes_divided_90 > 0 else 0)
    assists_per_90 = factory.LazyAttribute(lambda obj: (obj.assists / obj.minutes_divided_90) if obj.minutes_divided_90 > 0 else 0)
    total_goals_assists_per_90 = factory.LazyAttribute(lambda obj: obj.goal_per_90 + obj.assists_per_90)
    non_pk_goals_per_90 = factory.LazyAttribute(lambda obj: (obj.non_pk_goals / obj.minutes_divided_90) if obj.minutes_divided_90 > 0 else 0)
    non_pk_goal_and_assists_per_90 = factory.LazyAttribute(lambda obj: obj.non_pk_goals_per_90 + obj.assists_per_90)
    xg_per_90 = factory.LazyAttribute(lambda obj: (obj.xg / obj.minutes_divided_90) if obj.minutes_divided_90 > 0 else 0)
    xag_per_90 = factory.LazyAttribute(lambda obj: (obj.xag / obj.minutes_divided_90) if obj.minutes_divided_90 > 0 else 0)
    total_xg_xag_per_90 = factory.LazyAttribute(lambda obj: obj.xg_per_90 + obj.xag_per_90)
    non_pk_xg_per_90 = factory.LazyAttribute(lambda obj: (obj.non_pk_xg / obj.minutes_divided_90) if obj.minutes_divided_90 > 0 else 0)
    npxg_and_xag_per_90 = factory.LazyAttribute(lambda obj: obj.non_pk_xg_per_90 + obj.xag_per_90)
    points_added = fuzzy.FuzzyFloat(-10.0, 10.0)
    goal_value = fuzzy.FuzzyFloat(0.0, 5.0)
    pa_avg = fuzzy.FuzzyFloat(-0.5, 0.5)
    gv_avg = fuzzy.FuzzyFloat(0.0, 0.2)
    player = factory.SubFactory(PlayerFactory)
    season = factory.SubFactory(SeasonFactory)
    team = factory.SubFactory(TeamFactory)


class TeamStatsFactory(factory.Factory):
    """Factory for creating TeamStats test data."""
    class Meta:
        model = TeamStats
    
    fbref_url = factory.Sequence(lambda n: f"/en/squads/team_{n:08d}/stats/")
    goal_logs_url = factory.Sequence(lambda n: f"/en/squads/team_{n:08d}/goal-logs/")
    ranking = fuzzy.FuzzyInteger(1, 20)
    matches_played = fuzzy.FuzzyInteger(30, 38)
    wins = factory.LazyAttribute(lambda obj: fuzzy.FuzzyInteger(0, obj.matches_played).fuzz())
    draws = factory.LazyAttribute(lambda obj: fuzzy.FuzzyInteger(0, obj.matches_played - obj.wins).fuzz())
    losses = factory.LazyAttribute(lambda obj: obj.matches_played - obj.wins - obj.draws)
    goals_for = fuzzy.FuzzyInteger(20, 100)
    goals_against = fuzzy.FuzzyInteger(20, 100)
    goal_difference = factory.LazyAttribute(lambda obj: obj.goals_for - obj.goals_against)
    points = factory.LazyAttribute(lambda obj: (obj.wins * 3) + (obj.draws * 1))
    points_per_match = factory.LazyAttribute(lambda obj: obj.points / obj.matches_played if obj.matches_played > 0 else 0)
    xg = fuzzy.FuzzyFloat(20.0, 100.0)
    xga = fuzzy.FuzzyFloat(20.0, 100.0)
    xgd = factory.LazyAttribute(lambda obj: obj.xg - obj.xga)
    xgd_per_90 = factory.LazyAttribute(lambda obj: obj.xgd / (obj.matches_played * 90) * 90 if obj.matches_played > 0 else 0)
    team = factory.SubFactory(TeamFactory)
    season = factory.SubFactory(SeasonFactory)
