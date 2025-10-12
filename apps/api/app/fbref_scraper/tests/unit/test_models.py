"""Unit tests for database models."""

import pytest

from tests.utils.factories import (
    NationFactory, CompetitionFactory, SeasonFactory, TeamFactory,
    PlayerFactory, MatchFactory, EventFactory, PlayerStatsFactory,
    TeamStatsFactory
)


class TestNationModel:
    """Test Nation model functionality."""

    def test_nation_creation(self, db_session):
        """Test creating a nation."""
        nation = NationFactory()
        db_session.add(nation)
        db_session.commit()
        
        assert nation.id is not None
        assert nation.name is not None
        assert nation.country_code is not None
        assert nation.fbref_url is not None

    def test_nation_unique_constraints(self, db_session):
        """Test nation unique constraints."""
        nation1 = NationFactory(name="England", country_code="ENG")
        db_session.add(nation1)
        db_session.commit()
        
        nation2 = NationFactory(name="England", country_code="FRA", fbref_url="/en/countries/FRA/")
        db_session.add(nation2)
        
        with pytest.raises(Exception):
            db_session.commit()
        
        db_session.rollback()
        
        nation3 = NationFactory(name="France", country_code="ENG", fbref_url="/en/countries/ENG/")
        db_session.add(nation3)
        
        with pytest.raises(Exception):
            db_session.commit()

    def test_nation_relationships(self, db_session):
        """Test nation relationships."""
        nation = NationFactory()
        competition = CompetitionFactory(nation=nation)
        team = TeamFactory(nation=nation)
        
        db_session.add_all([nation, competition, team])
        db_session.commit()
        
        assert len(nation.competitions) == 1
        assert nation.competitions[0].name == competition.name
        assert len(nation.teams) == 1
        assert nation.teams[0].name == team.name


class TestCompetitionModel:
    """Test Competition model functionality."""

    def test_competition_creation(self, db_session):
        """Test creating a competition."""
        competition = CompetitionFactory()
        db_session.add(competition)
        db_session.commit()
        
        assert competition.id is not None
        assert competition.name is not None
        assert competition.fbref_id is not None
        assert competition.fbref_url is not None
        assert competition.nation_id is not None

    def test_competition_unique_constraints(self, db_session):
        """Test competition unique constraints."""
        competition1 = CompetitionFactory(fbref_id="comp_123")
        db_session.add(competition1)
        db_session.commit()
        
        competition2 = CompetitionFactory(fbref_id="comp_123")
        db_session.add(competition2)
        
        with pytest.raises(Exception):
            db_session.commit()


class TestSeasonModel:
    """Test Season model functionality."""

    def test_season_creation(self, db_session):
        """Test creating a season."""
        season = SeasonFactory()
        db_session.add(season)
        db_session.commit()
        
        assert season.id is not None
        assert season.start_year is not None
        assert season.end_year is not None
        assert season.end_year == season.start_year + 1
        assert season.fbref_url is not None
        assert season.competition_id is not None

    def test_season_url_generation(self, db_session):
        """Test season URL generation."""
        season = SeasonFactory(start_year=2023, end_year=2024)
        expected_url = "/en/seasons/2023-2024/"
        assert season.fbref_url == expected_url


class TestTeamModel:
    """Test Team model functionality."""

    def test_team_creation(self, db_session):
        """Test creating a team."""
        team = TeamFactory()
        db_session.add(team)
        db_session.commit()
        
        assert team.id is not None
        assert team.name is not None
        assert team.fbref_id is not None
        assert team.fbref_url is not None
        assert team.nation_id is not None

    def test_team_unique_constraints(self, db_session):
        """Test team unique constraints."""
        team1 = TeamFactory(fbref_id="team_123")
        db_session.add(team1)
        db_session.commit()
        
        team2 = TeamFactory(fbref_id="team_123")
        db_session.add(team2)
        
        with pytest.raises(Exception):
            db_session.commit()


class TestPlayerModel:
    """Test Player model functionality."""

    def test_player_creation(self, db_session):
        """Test creating a player."""
        player = PlayerFactory()
        db_session.add(player)
        db_session.commit()
        
        assert player.id is not None
        assert player.name is not None
        assert player.fbref_id is not None
        assert player.fbref_url is not None

    def test_player_unique_constraints(self, db_session):
        """Test player unique constraints."""
        player1 = PlayerFactory(fbref_id="player_123")
        db_session.add(player1)
        db_session.commit()
        
        player2 = PlayerFactory(fbref_id="player_123")
        db_session.add(player2)
        
        with pytest.raises(Exception):
            db_session.commit()


class TestMatchModel:
    """Test Match model functionality."""

    def test_match_creation(self, db_session):
        """Test creating a match."""
        match = MatchFactory()
        db_session.add(match)
        db_session.commit()
        
        assert match.id is not None
        assert match.home_team_goals is not None
        assert match.away_team_goals is not None
        assert match.date is not None
        assert match.fbref_id is not None
        assert match.fbref_url is not None
        assert match.season_id is not None
        assert match.home_team_id is not None
        assert match.away_team_id is not None

    def test_match_relationships(self, db_session):
        """Test match relationships."""
        match = MatchFactory()
        db_session.add(match)
        db_session.commit()
        
        assert match.season is not None
        assert match.home_team is not None
        assert match.away_team is not None
        assert match.home_team.id == match.home_team_id
        assert match.away_team.id == match.away_team_id


class TestEventModel:
    """Test Event model functionality."""

    def test_event_creation(self, db_session):
        """Test creating an event."""
        event = EventFactory()
        db_session.add(event)
        db_session.commit()
        
        assert event.id is not None
        assert event.event_type in ['goal', 'assist', 'own goal']
        assert event.minute is not None
        assert event.match_id is not None
        assert event.player_id is not None

    def test_event_unique_constraints(self, db_session):
        """Test event unique constraints."""
        event1 = EventFactory()
        db_session.add(event1)
        db_session.commit()
        
        event2 = EventFactory(
            match=event1.match,
            player=event1.player,
            minute=event1.minute,
            event_type=event1.event_type
        )
        db_session.add(event2)
        
        with pytest.raises(Exception):
            db_session.commit()


class TestPlayerStatsModel:
    """Test PlayerStats model functionality."""

    def test_player_stats_creation(self, db_session):
        """Test creating player stats."""
        player_stats = PlayerStatsFactory()
        db_session.add(player_stats)
        db_session.commit()
        
        assert player_stats.id is not None
        assert player_stats.matches_played is not None
        assert player_stats.player_id is not None
        assert player_stats.season_id is not None
        assert player_stats.team_id is not None

    def test_player_stats_calculations(self, db_session):
        """Test player stats calculations."""
        player_stats = PlayerStatsFactory(
            matches_played=20,
            goals_scored=10,
            assists=5
        )
        
        assert player_stats.total_goal_assists == 15
        assert player_stats.goal_per_90 > 0
        assert player_stats.assists_per_90 > 0

    def test_player_stats_unique_constraints(self, db_session):
        """Test player stats unique constraints."""
        player_stats1 = PlayerStatsFactory()
        db_session.add(player_stats1)
        db_session.commit()
        
        player_stats2 = PlayerStatsFactory(
            player=player_stats1.player,
            season=player_stats1.season,
            team=player_stats1.team
        )
        db_session.add(player_stats2)
        
        with pytest.raises(Exception):
            db_session.commit()


class TestTeamStatsModel:
    """Test TeamStats model functionality."""

    def test_team_stats_creation(self, db_session):
        """Test creating team stats."""
        team_stats = TeamStatsFactory()
        db_session.add(team_stats)
        db_session.commit()
        
        assert team_stats.id is not None
        assert team_stats.matches_played is not None
        assert team_stats.team_id is not None
        assert team_stats.season_id is not None

    def test_team_stats_calculations(self, db_session):
        """Test team stats calculations."""
        team_stats = TeamStatsFactory(
            matches_played=38,
            wins=20,
            draws=10
        )
        
        assert team_stats.losses == 8
        assert team_stats.points == 70
        assert team_stats.points_per_match == 70 / 38

    def test_team_stats_unique_constraints(self, db_session):
        """Test team stats unique constraints."""
        team_stats1 = TeamStatsFactory(fbref_url="/en/squads/team_123/stats/")
        db_session.add(team_stats1)
        db_session.commit()
        
        team_stats2 = TeamStatsFactory(fbref_url="/en/squads/team_123/stats/")
        db_session.add(team_stats2)
        
        with pytest.raises(Exception):
            db_session.commit()
