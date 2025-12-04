"""Unit tests for clubs service layer."""

from datetime import date

from app.services.clubs import (
    get_club_with_seasons,
    get_clubs_by_nation,
    get_team_season_goal_log,
    get_team_season_squad_stats,
    get_top_clubs_for_nation_core,
)
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
from app.tests.utils.service_helpers import (
    create_assist_event,
    create_basic_season_setup,
    create_goal_event,
)


class TestGetTopClubsForNationCore:
    """Test get_top_clubs_for_nation_core function."""

    def test_returns_top_clubs_sorted_by_avg_position(self, db_session):
        """Test that clubs are returned sorted by average position."""
        nation = NationFactory()
        comp = CompetitionFactory(name="Premier League", tier="1st", nation=nation)

        season1 = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp, start_year=2022, end_year=2023)

        team1 = TeamFactory(name="Arsenal", nation=nation)
        team2 = TeamFactory(name="Chelsea", nation=nation)
        team3 = TeamFactory(name="Liverpool", nation=nation)

        TeamStatsFactory(team=team1, season=season1, ranking=1)
        TeamStatsFactory(team=team1, season=season2, ranking=2)
        TeamStatsFactory(team=team2, season=season1, ranking=2)
        TeamStatsFactory(team=team2, season=season2, ranking=3)
        TeamStatsFactory(team=team3, season=season1, ranking=3)
        TeamStatsFactory(team=team3, season=season2, ranking=1)

        db_session.commit()

        result = get_top_clubs_for_nation_core(db_session, nation.id, limit=10, tier="1st")

        assert len(result) == 3
        assert result[0].name == "Arsenal"
        assert result[0].avg_position == 1.5
        assert result[1].name == "Liverpool"
        assert result[1].avg_position == 2.0
        assert result[2].name == "Chelsea"
        assert result[2].avg_position == 2.5

    def test_respects_limit_parameter(self, db_session):
        """Test that limit parameter is respected."""
        nation = NationFactory()
        comp = CompetitionFactory(name="Premier League", tier="1st", nation=nation)
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)

        for i in range(5):
            team = TeamFactory(name=f"Team {i}", nation=nation)
            TeamStatsFactory(team=team, season=season, ranking=i + 1)

        db_session.commit()

        result = get_top_clubs_for_nation_core(db_session, nation.id, limit=3, tier="1st")

        assert len(result) == 3

    def test_filters_by_tier(self, db_session):
        """Test that only teams from specified tier are included."""
        nation = NationFactory()
        tier1_competition = CompetitionFactory(name="Premier League", tier="1st", nation=nation)
        tier2_competition = CompetitionFactory(name="Championship", tier="2nd", nation=nation)

        season1 = SeasonFactory(competition=tier1_competition, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=tier2_competition, start_year=2023, end_year=2024)

        team1 = TeamFactory(name="Premier League Team", nation=nation)
        team2 = TeamFactory(name="Championship Team", nation=nation)

        TeamStatsFactory(team=team1, season=season1, ranking=1)
        TeamStatsFactory(team=team2, season=season2, ranking=1)

        db_session.commit()

        result = get_top_clubs_for_nation_core(db_session, nation.id, limit=10, tier="1st")

        assert len(result) == 1
        assert result[0].name == "Premier League Team"

    def test_excludes_teams_without_ranking(self, db_session):
        """Test that teams without ranking are excluded."""
        nation = NationFactory()
        comp = CompetitionFactory(name="Premier League", tier="1st", nation=nation)
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)

        team_with_ranking = TeamFactory(name="Team With Ranking", nation=nation)
        team_without_ranking = TeamFactory(name="Team Without Ranking", nation=nation)

        TeamStatsFactory(team=team_with_ranking, season=season, ranking=1)
        TeamStatsFactory(team=team_without_ranking, season=season, ranking=None)

        db_session.commit()

        result = get_top_clubs_for_nation_core(db_session, nation.id, limit=10, tier="1st")

        assert len(result) == 1
        assert result[0].name == "Team With Ranking"

    def test_sorts_by_name_when_avg_position_ties(self, db_session):
        """Test that teams with same avg position are sorted by name."""
        nation = NationFactory()
        comp = CompetitionFactory(name="Premier League", tier="1st", nation=nation)
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)

        team_a = TeamFactory(name="Arsenal", nation=nation)
        team_b = TeamFactory(name="Brighton", nation=nation)
        team_c = TeamFactory(name="Chelsea", nation=nation)

        TeamStatsFactory(team=team_a, season=season, ranking=1)
        TeamStatsFactory(team=team_b, season=season, ranking=1)
        TeamStatsFactory(team=team_c, season=season, ranking=1)

        db_session.commit()

        result = get_top_clubs_for_nation_core(db_session, nation.id, limit=10, tier="1st")

        assert len(result) == 3
        assert result[0].name == "Arsenal"
        assert result[1].name == "Brighton"
        assert result[2].name == "Chelsea"


class TestGetClubsByNation:
    """Test get_clubs_by_nation function."""

    def test_returns_top_clubs_per_nation(self, db_session):
        """Test that top clubs per nation are returned."""
        nation1 = NationFactory(name="England", country_code="ENG")
        nation2 = NationFactory(name="Spain", country_code="ESP")

        comp1 = CompetitionFactory(name="Premier League", tier="1st", nation=nation1)
        comp2 = CompetitionFactory(name="La Liga", tier="1st", nation=nation2)

        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp2, start_year=2023, end_year=2024)

        eng_team1 = TeamFactory(name="Arsenal", nation=nation1)
        eng_team2 = TeamFactory(name="Chelsea", nation=nation1)
        eng_team3 = TeamFactory(name="Liverpool", nation=nation1)

        esp_team1 = TeamFactory(name="Real Madrid", nation=nation2)
        esp_team2 = TeamFactory(name="Barcelona", nation=nation2)

        TeamStatsFactory(team=eng_team1, season=season1, ranking=1)
        TeamStatsFactory(team=eng_team2, season=season1, ranking=2)
        TeamStatsFactory(team=eng_team3, season=season1, ranking=3)
        TeamStatsFactory(team=esp_team1, season=season2, ranking=1)
        TeamStatsFactory(team=esp_team2, season=season2, ranking=2)

        db_session.commit()

        result = get_clubs_by_nation(db_session, limit_per_nation=2)

        assert len(result) == 2

        eng_result = next(r for r in result if r.nation.name == "England")
        assert len(eng_result.clubs) == 2
        assert eng_result.clubs[0].name == "Arsenal"
        assert eng_result.clubs[1].name == "Chelsea"

        esp_result = next(r for r in result if r.nation.name == "Spain")
        assert len(esp_result.clubs) == 2
        assert esp_result.clubs[0].name == "Real Madrid"
        assert esp_result.clubs[1].name == "Barcelona"

    def test_respects_limit_per_nation(self, db_session):
        """Test that limit_per_nation parameter is respected."""
        nation, _, season = create_basic_season_setup(db_session)

        for i in range(5):
            team = TeamFactory(name=f"Team {i}", nation=nation)
            TeamStatsFactory(team=team, season=season, ranking=i + 1)

        db_session.commit()

        result = get_clubs_by_nation(db_session, limit_per_nation=2)

        assert len(result) == 1
        assert len(result[0].clubs) == 2

    def test_only_includes_tier_1_teams(self, db_session):
        """Test that only tier 1 teams are included."""
        nation = NationFactory()
        tier1_comp = CompetitionFactory(name="Premier League", tier="1st", nation=nation)
        tier2_comp = CompetitionFactory(name="Championship", tier="2nd", nation=nation)

        season1 = SeasonFactory(competition=tier1_comp, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=tier2_comp, start_year=2023, end_year=2024)

        tier1_team = TeamFactory(name="Premier League Team", nation=nation)
        tier2_team = TeamFactory(name="Championship Team", nation=nation)

        TeamStatsFactory(team=tier1_team, season=season1, ranking=1)
        TeamStatsFactory(team=tier2_team, season=season2, ranking=1)

        db_session.commit()

        result = get_clubs_by_nation(db_session, limit_per_nation=5)

        assert len(result) == 1
        assert len(result[0].clubs) == 1
        assert result[0].clubs[0].name == "Premier League Team"

    def test_excludes_teams_without_ranking(self, db_session):
        """Test that teams without ranking are excluded."""
        nation, _, season = create_basic_season_setup(db_session)

        team_with_ranking = TeamFactory(name="Team With Ranking", nation=nation)
        team_without_ranking = TeamFactory(name="Team Without Ranking", nation=nation)

        TeamStatsFactory(team=team_with_ranking, season=season, ranking=1)
        TeamStatsFactory(team=team_without_ranking, season=season, ranking=None)

        db_session.commit()

        result = get_clubs_by_nation(db_session, limit_per_nation=5)

        assert len(result) == 1
        assert len(result[0].clubs) == 1
        assert result[0].clubs[0].name == "Team With Ranking"


class TestGetClubWithSeasons:
    """Test get_club_with_seasons function."""

    def test_returns_club_with_all_seasons(self, db_session):
        """Test that club with all season stats is returned."""
        nation = NationFactory(name="England", country_code="ENG")
        team = TeamFactory(name="Arsenal", nation=nation)

        comp1 = CompetitionFactory(name="Premier League", tier="1st", nation=nation)
        comp2 = CompetitionFactory(name="Premier League", tier="1st", nation=nation)

        season1 = SeasonFactory(competition=comp1, start_year=2023, end_year=2024)
        season2 = SeasonFactory(competition=comp1, start_year=2022, end_year=2023)
        season3 = SeasonFactory(competition=comp2, start_year=2024, end_year=2025)

        TeamStatsFactory(team=team, season=season1, ranking=1, matches_played=38, wins=30)
        TeamStatsFactory(team=team, season=season2, ranking=2, matches_played=38, wins=28)
        TeamStatsFactory(team=team, season=season3, ranking=1, matches_played=10, wins=8)

        db_session.commit()

        club_info, seasons_data = get_club_with_seasons(db_session, team.id)

        assert club_info is not None
        assert club_info.id == team.id
        assert club_info.name == "Arsenal"
        assert club_info.nation.name == "England"
        assert len(seasons_data) == 3

        assert seasons_data[0].season.start_year == 2024
        assert seasons_data[0].competition.name == "Premier League"
        assert seasons_data[1].season.start_year == 2023
        assert seasons_data[1].competition.name == "Premier League"
        assert seasons_data[2].season.start_year == 2022
        assert seasons_data[2].competition.name == "Premier League"

    def test_returns_none_when_club_not_found(self, db_session):
        """Test that None is returned when club doesn't exist."""
        club_info, seasons_data = get_club_with_seasons(db_session, 99999)

        assert club_info is None
        assert seasons_data == []

    def test_returns_empty_seasons_when_no_stats(self, db_session):
        """Test that empty seasons list is returned when club has no stats."""
        nation = NationFactory()
        team = TeamFactory(name="Arsenal", nation=nation)
        db_session.commit()

        club_info, seasons_data = get_club_with_seasons(db_session, team.id)

        assert club_info is not None
        assert club_info.id == team.id
        assert seasons_data == []

    def test_includes_all_team_stats_fields(self, db_session):
        """Test that all team stats fields are included."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)

        team_stats = TeamStatsFactory(
            team=team,
            season=season,
            ranking=1,
            matches_played=38,
            wins=30,
            draws=5,
            losses=3,
            goals_for=90,
            goals_against=30,
            goal_difference=60,
            points=95,
            attendance=60000,
            notes="Champions",
        )

        db_session.commit()

        _, seasons_data = get_club_with_seasons(db_session, team.id)

        assert len(seasons_data) == 1
        stats = seasons_data[0].stats
        assert stats.ranking == team_stats.ranking
        assert stats.matches_played == team_stats.matches_played
        assert stats.wins == team_stats.wins
        assert stats.draws == team_stats.draws
        assert stats.losses == team_stats.losses
        assert stats.goals_for == team_stats.goals_for
        assert stats.goals_against == team_stats.goals_against
        assert stats.goal_difference == team_stats.goal_difference
        assert stats.points == team_stats.points
        assert stats.attendance == team_stats.attendance
        assert stats.notes == team_stats.notes


class TestGetTeamSeasonSquadStats:
    """Test get_team_season_squad_stats function."""

    def test_returns_squad_with_player_stats(self, db_session):
        """Test that squad with player stats is returned."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)

        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)
        player3 = PlayerFactory(name="Player 3", nation=nation)

        PlayerStatsFactory(
            team=team, season=season, player=player1, goal_value=5.0, goals_scored=10, assists=5
        )
        PlayerStatsFactory(
            team=team, season=season, player=player2, goal_value=3.0, goals_scored=5, assists=3
        )
        PlayerStatsFactory(
            team=team, season=season, player=player3, goal_value=2.0, goals_scored=2, assists=1
        )

        db_session.commit()

        club_info, season_display, competition_display, players_data = get_team_season_squad_stats(
            db_session, team.id, season.id
        )

        assert club_info is not None
        assert club_info.id == team.id
        assert season_display is not None
        assert season_display.start_year == 2023
        assert competition_display is not None
        assert competition_display.name == "Premier League"
        assert len(players_data) == 3

        assert players_data[0].player.name == "Player 1"
        assert players_data[0].stats.goal_value == 5.0
        assert players_data[1].player.name == "Player 2"
        assert players_data[1].stats.goal_value == 3.0
        assert players_data[2].player.name == "Player 3"
        assert players_data[2].stats.goal_value == 2.0

    def test_returns_none_when_team_not_found(self, db_session):
        """Test that None is returned when team doesn't exist."""
        comp = CompetitionFactory()
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        db_session.commit()

        club_info, season_display, competition_display, players_data = get_team_season_squad_stats(
            db_session, 99999, season.id
        )

        assert club_info is None
        assert season_display is None
        assert competition_display is None
        assert players_data == []

    def test_returns_none_when_season_not_found(self, db_session):
        """Test that None is returned when season doesn't exist."""
        nation = NationFactory()
        team = TeamFactory(name="Arsenal", nation=nation)
        db_session.commit()

        club_info, season_display, competition_display, players_data = get_team_season_squad_stats(
            db_session, team.id, 99999
        )

        assert club_info is None
        assert season_display is None
        assert competition_display is None
        assert players_data == []

    def test_returns_empty_list_when_no_player_stats(self, db_session):
        """Test that empty list is returned when no player stats exist."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)
        db_session.commit()

        club_info, season_display, _, players_data = get_team_season_squad_stats(
            db_session, team.id, season.id
        )

        assert club_info is not None
        assert season_display is not None
        assert players_data == []

    def test_only_includes_players_for_specified_team_and_season(self, db_session):
        """Test that only players for specified team and season are included."""
        nation, comp, season1 = create_basic_season_setup(db_session)
        team1 = TeamFactory(name="Arsenal", nation=nation)
        team2 = TeamFactory(name="Chelsea", nation=nation)
        season2 = SeasonFactory(competition=comp, start_year=2022, end_year=2023)

        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)

        PlayerStatsFactory(team=team1, season=season1, player=player1, goal_value=5.0)
        PlayerStatsFactory(team=team2, season=season1, player=player1, goal_value=3.0)
        PlayerStatsFactory(team=team1, season=season2, player=player2, goal_value=2.0)

        db_session.commit()

        _, _, _, players_data = get_team_season_squad_stats(db_session, team1.id, season1.id)

        assert len(players_data) == 1
        assert players_data[0].player.name == "Player 1"
        assert players_data[0].stats.goal_value == 5.0


class TestGetTeamSeasonGoalLog:
    """Test get_team_season_goal_log function."""

    def test_returns_goal_log_for_team_season(self, db_session):
        """Test that goal log for team season is returned."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)
        opponent = TeamFactory(name="Chelsea", nation=nation)
        player = PlayerFactory(name="Scorer", nation=nation)

        match = MatchFactory(
            home_team=team,
            away_team=opponent,
            season=season,
            date=date(2023, 9, 1),
            home_team_goals=2,
            away_team_goals=1,
        )

        _ = create_goal_event(
            match,
            player,
            minute=10,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            goal_value=0.5,
            xg=0.3,
            post_shot_xg=0.4,
        )

        db_session.commit()

        club_info, season_display, competition_display, goal_entries = get_team_season_goal_log(
            db_session, team.id, season.id
        )

        assert club_info is not None
        assert club_info.id == team.id
        assert season_display is not None
        assert season_display.start_year == 2023
        assert competition_display is not None
        assert competition_display.name == "Premier League"
        assert len(goal_entries) == 1

        goal = goal_entries[0]
        assert goal.scorer.name == "Scorer"
        assert goal.opponent.name == "Chelsea"
        assert goal.minute == 10
        assert goal.goal_value == 0.5
        assert goal.xg == 0.3
        assert goal.post_shot_xg == 0.4

    def test_includes_own_goals(self, db_session):
        """Test that own goals are included."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)
        opponent = TeamFactory(name="Chelsea", nation=nation)
        player = PlayerFactory(name="Scorer", nation=nation)

        match = MatchFactory(
            home_team=team, away_team=opponent, season=season, date=date(2023, 9, 1)
        )

        _ = create_goal_event(
            match,
            player,
            minute=10,
            home_pre=0,
            home_post=1,
            away_pre=0,
            away_post=0,
            event_type="own goal",
        )

        db_session.commit()

        _, _, _, goal_entries = get_team_season_goal_log(db_session, team.id, season.id)

        assert len(goal_entries) == 1
        assert goal_entries[0].scorer.name == "Scorer (OG)"

    def test_includes_assists_when_present(self, db_session):
        """Test that assists are included when present."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)
        opponent = TeamFactory(name="Chelsea", nation=nation)
        scorer = PlayerFactory(name="Scorer", nation=nation)
        assister = PlayerFactory(name="Assister", nation=nation)

        match = MatchFactory(
            home_team=team, away_team=opponent, season=season, date=date(2023, 9, 1)
        )

        _ = create_goal_event(
            match, scorer, minute=10, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        _ = create_assist_event(
            match, assister, minute=10, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        db_session.commit()

        _, _, _, goal_entries = get_team_season_goal_log(db_session, team.id, season.id)

        assert len(goal_entries) == 1
        assert goal_entries[0].assisted_by is not None
        assert goal_entries[0].assisted_by.name == "Assister"

    def test_returns_none_when_team_not_found(self, db_session):
        """Test that None is returned when team doesn't exist."""
        comp = CompetitionFactory()
        season = SeasonFactory(competition=comp, start_year=2023, end_year=2024)
        db_session.commit()

        club_info, season_display, competition_display, goal_entries = get_team_season_goal_log(
            db_session, 99999, season.id
        )

        assert club_info is None
        assert season_display is None
        assert competition_display is None
        assert goal_entries == []

    def test_returns_none_when_season_not_found(self, db_session):
        """Test that None is returned when season doesn't exist."""
        nation = NationFactory()
        team = TeamFactory(name="Arsenal", nation=nation)
        db_session.commit()

        club_info, season_display, competition_display, goal_entries = get_team_season_goal_log(
            db_session, team.id, 99999
        )

        assert club_info is None
        assert season_display is None
        assert competition_display is None
        assert goal_entries == []

    def test_returns_empty_list_when_no_goals(self, db_session):
        """Test that empty list is returned when no goals exist."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)
        opponent = TeamFactory(name="Chelsea", nation=nation)

        match = MatchFactory(
            home_team=team, away_team=opponent, season=season, date=date(2023, 9, 1)
        )

        EventFactory(match=match, event_type="yellow card", minute=10)

        db_session.commit()

        club_info, season_display, _, goal_entries = get_team_season_goal_log(
            db_session, team.id, season.id
        )

        assert club_info is not None
        assert season_display is not None
        assert goal_entries == []

    def test_only_includes_goals_for_specified_team(self, db_session):
        """Test that only goals for specified team are included."""
        nation, _, season = create_basic_season_setup(db_session)
        team1 = TeamFactory(name="Arsenal", nation=nation)
        team2 = TeamFactory(name="Chelsea", nation=nation)
        player1 = PlayerFactory(name="Player 1", nation=nation)
        player2 = PlayerFactory(name="Player 2", nation=nation)

        match = MatchFactory(home_team=team1, away_team=team2, season=season, date=date(2023, 9, 1))

        create_goal_event(
            match, player1, minute=10, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        create_goal_event(
            match, player2, minute=20, home_pre=1, home_post=1, away_pre=0, away_post=1
        )

        db_session.commit()

        _, _, _, goal_entries = get_team_season_goal_log(db_session, team1.id, season.id)

        assert len(goal_entries) == 1
        assert goal_entries[0].scorer.name == "Player 1"
        assert goal_entries[0].minute == 10

    def test_handles_away_team_goals(self, db_session):
        """Test that away team goals are included when team is away."""
        nation, _, season = create_basic_season_setup(db_session)
        team = TeamFactory(name="Arsenal", nation=nation)
        opponent = TeamFactory(name="Chelsea", nation=nation)
        player = PlayerFactory(name="Scorer", nation=nation)

        match = MatchFactory(
            home_team=opponent, away_team=team, season=season, date=date(2023, 9, 1)
        )

        _ = create_goal_event(
            match, player, minute=10, home_pre=0, home_post=0, away_pre=0, away_post=1
        )

        db_session.commit()

        _, _, _, goal_entries = get_team_season_goal_log(db_session, team.id, season.id)

        assert len(goal_entries) == 1
        assert goal_entries[0].scorer.name == "Scorer"
        assert goal_entries[0].venue == "Away"
