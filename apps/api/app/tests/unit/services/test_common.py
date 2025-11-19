"""Unit tests for common service utilities."""

import pytest
from sqlalchemy.sql.elements import BooleanClauseList
from app.services.common import (
    format_season_display_name,
    build_nation_info,
    normalize_season_years,
    calculate_goal_value_avg,
    build_season_filter_for_all_leagues,
    build_club_info,
)
from app.schemas.common import NationInfo
from app.schemas.clubs import ClubInfo, NationDetailed
from app.tests.utils.factories import NationFactory, TeamFactory


def create_england_nation(db_session):
    """Helper to create an England nation for testing."""
    nation = NationFactory(
        id=1,
        name="England",
        country_code="ENG"
    )
    db_session.commit()
    return nation


class TestFormatSeasonDisplayName:
    """Test format_season_display_name function."""

    def test_format_season_with_different_years(self):
        """Test formatting season with different start and end years."""
        result = format_season_display_name(2020, 2021)
        assert result == "2020/2021"

    def test_format_season_with_same_years(self):
        """Test formatting season with same start and end year."""
        result = format_season_display_name(2020, 2020)
        assert result == "2020"

    def test_format_season_with_none_end_year(self):
        """Test formatting season with None end year."""
        result = format_season_display_name(2020, None)
        assert result == "2020"


class TestBuildNationInfo:
    """Test build_nation_info function."""

    def test_build_nation_info_with_nation(self, db_session):
        """Test building NationInfo from a Nation model."""
        nation = create_england_nation(db_session)

        result = build_nation_info(nation)

        assert result is not None
        assert isinstance(result, NationInfo)
        assert result.id == 1
        assert result.name == "England"
        assert result.country_code == "ENG"

    def test_build_nation_info_with_none(self):
        """Test building NationInfo with None input."""
        result = build_nation_info(None)
        assert result is None


class TestNormalizeSeasonYears:
    """Test normalize_season_years function."""

    def test_normalize_european_season(self):
        """Test normalizing European season (different years)."""
        result = normalize_season_years(2020, 2021)
        assert result == (2020, 2021)

    def test_normalize_single_year_season(self):
        """Test normalizing single year season."""
        result = normalize_season_years(2023, 2023)
        assert result == (2022, 2023)


class TestCalculateGoalValueAvg:
    """Test calculate_goal_value_avg function."""

    @pytest.mark.parametrize("total_value,total_goals,expected", [
        (10.0, 5, 2.0),  # Valid data
        (7.5, 3, 2.5),  # Float result
        (10.0, 0, None),  # Zero goals
        (10.0, None, None),  # None total_goals
        (None, 5, None),  # None total_goal_value
        (0.0, 5, None),  # Zero goal value
        (None, None, None),  # Both None
    ])
    def test_calculate_goal_value_avg(self, total_value, total_goals, expected):
        """Test calculating goal value average with various inputs."""
        result = calculate_goal_value_avg(total_value, total_goals)
        assert result == expected

    def test_calculate_avg_precision(self):
        """Test that average maintains precision."""
        result = calculate_goal_value_avg(1.0, 3)
        assert abs(result - 0.3333333333333333) < 0.0001


class TestBuildSeasonFilterForAllLeagues:
    """Test build_season_filter_for_all_leagues function."""

    def test_build_season_filter_creates_or_clause(self):
        """Test that filter creates an OR clause with two conditions."""
        result = build_season_filter_for_all_leagues(2020, 2021)

        assert isinstance(result, BooleanClauseList)
        assert hasattr(result, 'clauses')
        assert len(result.clauses) == 2


class TestBuildClubInfo:
    """Test build_club_info function."""

    def test_build_club_info_with_team_and_nation(self, db_session):
        """Test building ClubInfo from Team with nation."""
        nation = create_england_nation(db_session)
        team = TeamFactory(
            id=1,
            name="Arsenal",
            nation=nation
        )
        db_session.commit()

        result = build_club_info(team)

        assert isinstance(result, ClubInfo)
        assert result.id == 1
        assert result.name == "Arsenal"
        assert isinstance(result.nation, NationDetailed)
        assert result.nation.id == 1
        assert result.nation.name == "England"
        assert result.nation.country_code == "ENG"

    def test_build_club_info_with_team_without_nation(self, db_session):
        """Test building ClubInfo from Team without nation."""
        team = TeamFactory(
            id=2,
            name="Unknown Team",
            nation=None
        )
        db_session.commit()

        result = build_club_info(team)

        assert isinstance(result, ClubInfo)
        assert result.id == 2
        assert result.name == "Unknown Team"
        assert isinstance(result.nation, NationDetailed)
        assert result.nation.id is None
        assert result.nation.name == "Unknown"
        assert result.nation.country_code is None
