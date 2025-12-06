"""Unit tests for leagues service layer."""

from app.services.leagues import (
    format_season_range,
    get_all_leagues_with_season_ranges,
    get_all_unique_seasons,
    get_league_seasons,
    get_league_table_for_season,
)
from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)
from app.tests.utils.helpers import create_basic_season_setup


class TestFormatSeasonRange:
    """Tests for format_season_range function."""

    def test_returns_no_seasons_message_when_empty(self):
        """Test that 'No seasons available' is returned when list is empty."""
        result = format_season_range([])

        assert result == "No seasons available"

    def test_formats_single_season(self):
        """Test formatting a single season."""
        season = SeasonFactory.build(start_year=2023, end_year=2024)
        result = format_season_range([season])

        assert result == "2023/2024 - 2023/2024"

    def test_formats_multiple_seasons(self):
        """Test formatting multiple seasons."""
        season1 = SeasonFactory.build(start_year=2022, end_year=2023)
        season2 = SeasonFactory.build(start_year=2023, end_year=2024)
        season3 = SeasonFactory.build(start_year=2024, end_year=2025)

        result = format_season_range([season3, season1, season2])

        assert result == "2022/2023 - 2024/2025"

    def test_formats_brazilian_seasons(self):
        """Test formatting Brazilian single-year seasons."""
        season1 = SeasonFactory.build(start_year=2023, end_year=2023)
        season2 = SeasonFactory.build(start_year=2024, end_year=2024)

        result = format_season_range([season2, season1])

        assert result == "2023 - 2024"

    def test_formats_mixed_season_types(self):
        """Test formatting mix of European and Brazilian seasons."""
        season1 = SeasonFactory.build(start_year=2022, end_year=2023)
        season2 = SeasonFactory.build(start_year=2023, end_year=2023)
        season3 = SeasonFactory.build(start_year=2024, end_year=2025)

        result = format_season_range([season3, season1, season2])

        assert result == "2022/2023 - 2024/2025"


class TestGetAllLeaguesWithSeasonRanges:
    """Tests for get_all_leagues_with_season_ranges function."""

    def test_returns_all_leagues_with_season_ranges(self, db_session):
        """Test that all leagues are returned with season ranges."""
        nation1 = NationFactory(name="England", country_code="ENG")
        nation2 = NationFactory(name="Spain", country_code="ESP")

        comp1 = CompetitionFactory(name="Premier League", nation=nation1, tier="1st")
        comp2 = CompetitionFactory(name="La Liga", nation=nation2, tier="1st")

        SeasonFactory(competition=comp1, start_year=2022, end_year=2023)
        SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        SeasonFactory(competition=comp2, start_year=2023, end_year=2024)

        db_session.commit()

        result = get_all_leagues_with_season_ranges(db_session)

        assert len(result) == 2
        assert any(league.name == "Premier League" for league in result)
        assert any(league.name == "La Liga" for league in result)

    def test_sorts_by_country_and_tier(self, db_session):
        """Test that leagues are sorted by country and tier."""
        nation1 = NationFactory(name="England", country_code="ENG")
        nation2 = NationFactory(name="Spain", country_code="ESP")

        comp1 = CompetitionFactory(name="Premier League", nation=nation1, tier="1st")
        comp2 = CompetitionFactory(name="Championship", nation=nation1, tier="2nd")
        comp3 = CompetitionFactory(name="La Liga", nation=nation2, tier="1st")

        SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        SeasonFactory(competition=comp2, start_year=2023, end_year=2024)
        SeasonFactory(competition=comp3, start_year=2023, end_year=2024)

        db_session.commit()

        result = get_all_leagues_with_season_ranges(db_session)

        assert len(result) == 3
        assert result[0].country == "England"
        assert result[0].tier == "1st"
        assert result[1].country == "England"
        assert result[1].tier == "2nd"
        assert result[2].country == "Spain"

    def test_includes_available_seasons_string(self, db_session):
        """Test that available_seasons string is included."""
        nation, comp, season = create_basic_season_setup(db_session)
        SeasonFactory(competition=comp, start_year=2022, end_year=2023)

        db_session.commit()

        result = get_all_leagues_with_season_ranges(db_session)

        assert len(result) == 1
        assert "2022/2023" in result[0].available_seasons
        assert "2023/2024" in result[0].available_seasons

    def test_handles_competitions_without_seasons(self, db_session):
        """Test that competitions without seasons are handled correctly."""
        nation = NationFactory()
        CompetitionFactory(name="New League", nation=nation)

        db_session.commit()

        result = get_all_leagues_with_season_ranges(db_session)

        assert len(result) == 1
        assert result[0].available_seasons == "No seasons available"


class TestGetLeagueSeasons:
    """Tests for get_league_seasons function."""

    def test_returns_seasons_for_league_sorted_descending(self, db_session):
        """Test that seasons are returned sorted by start_year descending."""
        nation, comp, _ = create_basic_season_setup(db_session)
        SeasonFactory(competition=comp, start_year=2021, end_year=2022)
        SeasonFactory(competition=comp, start_year=2022, end_year=2023)

        db_session.commit()

        result = get_league_seasons(db_session, comp.id)

        assert len(result) == 3
        assert result[0].start_year == 2023
        assert result[1].start_year == 2022
        assert result[2].start_year == 2021

    def test_returns_empty_list_when_no_seasons(self, db_session):
        """Test that empty list is returned when league has no seasons."""
        nation = NationFactory()
        comp = CompetitionFactory(name="New League", nation=nation)

        db_session.commit()

        result = get_league_seasons(db_session, comp.id)

        assert result == []


class TestGetAllUniqueSeasons:
    """Tests for get_all_unique_seasons function."""

    def test_returns_unique_seasons_normalized(self, db_session):
        """Test that unique seasons are returned with normalization."""
        nation = NationFactory()
        comp1 = CompetitionFactory(nation=nation)
        comp2 = CompetitionFactory(nation=nation)

        SeasonFactory(competition=comp1, start_year=2022, end_year=2023)
        SeasonFactory(competition=comp2, start_year=2022, end_year=2023)
        SeasonFactory(competition=comp1, start_year=2023, end_year=2024)

        db_session.commit()

        result = get_all_unique_seasons(db_session)

        assert len(result) >= 2
        assert any(season.start_year == 2022 and season.end_year == 2023 for season in result)
        assert any(season.start_year == 2023 and season.end_year == 2024 for season in result)

    def test_normalizes_brazilian_seasons(self, db_session):
        """Test that Brazilian single-year seasons are normalized."""
        nation = NationFactory()
        comp = CompetitionFactory(nation=nation)

        SeasonFactory(competition=comp, start_year=2023, end_year=2023)

        db_session.commit()

        result = get_all_unique_seasons(db_session)

        assert len(result) >= 1
        brazilian_season = next((s for s in result if s.display_name == "2022/2023"), None)
        assert brazilian_season is not None

    def test_sorts_seasons_descending(self, db_session):
        """Test that seasons are sorted by start_year descending."""
        nation = NationFactory()
        comp = CompetitionFactory(nation=nation)

        SeasonFactory(competition=comp, start_year=2021, end_year=2022)
        SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        SeasonFactory(competition=comp, start_year=2022, end_year=2023)

        db_session.commit()

        result = get_all_unique_seasons(db_session)

        assert len(result) >= 3
        start_years = [s.start_year for s in result if s.start_year in [2021, 2022, 2023]]
        assert start_years == sorted(start_years, reverse=True)

    def test_removes_duplicate_display_names(self, db_session):
        """Test that duplicate display names are removed."""
        nation = NationFactory()
        comp1 = CompetitionFactory(nation=nation)
        comp2 = CompetitionFactory(nation=nation)

        SeasonFactory(competition=comp1, start_year=2022, end_year=2023)
        SeasonFactory(competition=comp2, start_year=2022, end_year=2023)

        db_session.commit()

        result = get_all_unique_seasons(db_session)

        display_names = [s.display_name for s in result]
        assert len(display_names) == len(set(display_names))


class TestGetLeagueTableForSeason:
    """Tests for get_league_table_for_season function."""

    def test_returns_league_table_sorted_by_ranking(self, db_session):
        """Test that league table is returned sorted by ranking."""
        nation, comp, season = create_basic_season_setup(db_session)

        team1 = TeamFactory(name="Team 1", nation=nation)
        team2 = TeamFactory(name="Team 2", nation=nation)
        team3 = TeamFactory(name="Team 3", nation=nation)

        TeamStatsFactory(
            team=team1, season=season, ranking=1, matches_played=38, wins=30, points=90
        )
        TeamStatsFactory(
            team=team2, season=season, ranking=2, matches_played=38, wins=25, points=75
        )
        TeamStatsFactory(
            team=team3, season=season, ranking=3, matches_played=38, wins=20, points=60
        )

        db_session.commit()

        league_info, season_info, table = get_league_table_for_season(
            db_session, comp.id, season.id
        )

        assert league_info is not None
        assert league_info.name == "Premier League"
        assert season_info is not None
        assert len(table) == 3
        assert table[0].position == 1
        assert table[0].team_name == "Team 1"
        assert table[1].position == 2
        assert table[1].team_name == "Team 2"
        assert table[2].position == 3
        assert table[2].team_name == "Team 3"

    def test_includes_all_team_stats(self, db_session):
        """Test that all team stats are included in table entries."""
        nation, comp, season = create_basic_season_setup(db_session)
        team = TeamFactory(nation=nation)

        TeamStatsFactory(
            team=team,
            season=season,
            ranking=1,
            matches_played=38,
            wins=30,
            draws=5,
            losses=3,
            goals_for=85,
            goals_against=30,
            goal_difference=55,
            points=95,
        )

        db_session.commit()

        _, _, table = get_league_table_for_season(db_session, comp.id, season.id)

        assert len(table) == 1
        entry = table[0]
        assert entry.matches_played == 38
        assert entry.wins == 30
        assert entry.draws == 5
        assert entry.losses == 3
        assert entry.goals_for == 85
        assert entry.goals_against == 30
        assert entry.goal_difference == 55
        assert entry.points == 95

    def test_returns_none_when_competition_not_found(self, db_session):
        """Test that None is returned when competition doesn't exist."""
        _, _, season = create_basic_season_setup(db_session)

        league_info, season_info, table = get_league_table_for_season(db_session, 99999, season.id)

        assert league_info is None
        assert season_info is None
        assert table == []

    def test_returns_none_when_season_not_found(self, db_session):
        """Test that league_info is returned but season_info is None when season doesn't exist."""
        nation, comp, _ = create_basic_season_setup(db_session)

        league_info, season_info, table = get_league_table_for_season(db_session, comp.id, 99999)

        assert league_info is not None
        assert league_info.id == comp.id
        assert league_info.name == comp.name
        assert season_info is None
        assert table == []

    def test_returns_none_when_season_not_for_league(self, db_session):
        """Test that league_info is returned but season_info is None when season doesn't belong to league."""
        nation = NationFactory()
        comp1 = CompetitionFactory(nation=nation)
        comp2 = CompetitionFactory(nation=nation)
        SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)

        db_session.commit()

        league_info, season_info, table = get_league_table_for_season(
            db_session, comp1.id, season2.id
        )

        assert league_info is not None
        assert league_info.id == comp1.id
        assert league_info.name == comp1.name
        assert season_info is None
        assert table == []

    def test_handles_empty_table(self, db_session):
        """Test that empty table is returned when no team stats exist."""
        nation, comp, season = create_basic_season_setup(db_session)

        db_session.commit()

        league_info, season_info, table = get_league_table_for_season(
            db_session, comp.id, season.id
        )

        assert league_info is not None
        assert season_info is not None
        assert table == []

    def test_includes_league_info_with_country(self, db_session):
        """Test that league info includes country name."""
        nation = NationFactory(name="England", country_code="ENG")
        comp = CompetitionFactory(name="Premier League", nation=nation)
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)

        db_session.commit()

        league_info, _, _ = get_league_table_for_season(db_session, comp.id, season.id)

        assert league_info is not None
        assert league_info.name == "Premier League"
        assert league_info.country == "England"

    def test_handles_competition_without_nation(self, db_session):
        """Test that competition without nation shows 'Unknown' country."""
        comp = CompetitionFactory(name="International League", nation=None)
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)

        db_session.commit()

        league_info, _, _ = get_league_table_for_season(db_session, comp.id, season.id)

        assert league_info is not None
        assert league_info.country == "Unknown"
