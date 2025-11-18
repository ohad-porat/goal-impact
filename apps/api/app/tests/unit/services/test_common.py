"""Unit tests for common service utilities."""

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
        nation = NationFactory(
            id=1,
            name="England",
            country_code="ENG"
        )
        db_session.commit()

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

    def test_calculate_avg_with_valid_data(self):
        """Test calculating average with valid data."""
        result = calculate_goal_value_avg(10.0, 5)
        assert result == 2.0

    def test_calculate_avg_with_float_result(self):
        """Test calculating average that results in float."""
        result = calculate_goal_value_avg(7.5, 3)
        assert result == 2.5

    def test_calculate_avg_returns_none_with_zero_goals(self):
        """Test that average returns None when total_goals is 0."""
        result = calculate_goal_value_avg(10.0, 0)
        assert result is None

    def test_calculate_avg_returns_none_with_none_total_goals(self):
        """Test that average returns None when total_goals is None."""
        result = calculate_goal_value_avg(10.0, None)
        assert result is None

    def test_calculate_avg_returns_none_with_none_total_goal_value(self):
        """Test that average returns None when total_goal_value is None."""
        result = calculate_goal_value_avg(None, 5)
        assert result is None

    def test_calculate_avg_returns_none_with_zero_goal_value(self):
        """Test that average returns None when total_goal_value is 0."""
        result = calculate_goal_value_avg(0.0, 5)
        assert result is None

    def test_calculate_avg_with_both_none(self):
        """Test that average returns None when both values are None."""
        result = calculate_goal_value_avg(None, None)
        assert result is None

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
        nation = NationFactory(
            id=1,
            name="England",
            country_code="ENG"
        )
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
