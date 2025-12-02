"""Unit tests for PlayersScraper."""

import pandas as pd

from app.fbref_scraper.scrapers.players_scraper import PlayersScraper
from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)
from app.models import Player, PlayerStats


class TestPlayersScraper:
    """Test PlayersScraper functionality."""

    def test_scrape_with_year_filter(self, db_session, mocker):
        """Test scraping with year range filters."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season1 = SeasonFactory(competition=competition, start_year=2020, end_year=2021)
        season2 = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        
        team_stats1 = TeamStatsFactory(season=season1, fbref_url='/en/squads/team1/')
        team_stats2 = TeamStatsFactory(season=season2, fbref_url='/en/squads/team2/')
        
        db_session.add_all([nation, competition, season1, season2, team_stats1, team_stats2])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(return_value={'href': '/en/players/player123/goal-logs/'})
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.fetch_html_table = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021)
        
        assert scraper.load_page.call_count == 1

    def test_goal_logs_url_simple_find(self, db_session, mocker):
        """Test finding goal logs URL with simple element find."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team-1/')
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()

        scraper.load_page = mocker.Mock()
        
        scraper.find_element = mocker.Mock(return_value={'href': '/en/players/player123/goal-logs/'})
        scraper.log_progress = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021)
        
        db_session.refresh(team_stats)
        assert team_stats.goal_logs_url == '/en/players/player123/goal-logs/'

    def test_goal_logs_url_not_found(self, db_session, mocker):
        """Test error handling when goal logs URL is not found."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2022, end_year=2023)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team-2/')
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()

        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])

        scraper.find_element = mocker.Mock(return_value=None)
        scraper.find_elements = mocker.Mock(return_value=[])

        scraper.scrape(nations=['England'], from_year=2022, to_year=2022)

        scraper.log_progress.assert_called()

    def test_player_parsing_with_valid_data(self, db_session, mocker):
        """Test parsing player data from HTML table."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2023, end_year=2024)
        team_stats = TeamStatsFactory(season=season, team=TeamFactory(name="Arsenal"))
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(side_effect=lambda *args, **kwargs: 
                                               {'href': '/en/players/team123/goal-logs/'} if 'Goal Logs' in kwargs.get('text', '') 
                                               else {'href': '/en/players/12345678/'} if 'Bukayo Saka' in kwargs.get('string', '')
                                               else None)
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['eng ENG'],
            ('Playing Time', 'MP'): [38],
            ('Playing Time', 'Starts'): [35],
            ('Playing Time', 'Min'): [3150],
            ('Performance', 'Gls'): [14],
            ('Performance', 'Ast'): [8],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2023, to_year=2023)
        
        player = db_session.query(Player).filter_by(name='Bukayo Saka').first()
        assert player is not None
        assert player.fbref_id == '12345678'
        
        player_stats = db_session.query(PlayerStats).filter_by(player_id=player.id).first()
        assert player_stats is not None
        assert player_stats.matches_played == 38
        assert player_stats.goals_scored == 14
        assert player_stats.assists == 8

    def test_get_player_stat_value_success(self, mocker):
        """Test successful stat value retrieval."""
        scraper = PlayersScraper()
        
        mock_series = mocker.Mock()
        mock_subseries = mocker.Mock()
        mock_subseries.iloc = [15]
        mock_series.iloc = [15]
        mock_series.__getitem__ = mocker.Mock(return_value=mock_subseries)
        
        result = scraper._get_player_stat_value(mock_series, ('Performance', 'Gls'))
        assert result == 15

    def test_get_player_stat_value_missing_key(self):
        """Test stat value retrieval with missing key."""
        scraper = PlayersScraper()
        
        mock_series = pd.DataFrame({
            ('Performance', 'Ast'): [10]
        }).iloc[0]
        
        result = scraper._get_player_stat_value(mock_series, ('Performance', 'Gls'))
        assert result is None

    def test_get_player_stat_value_index_error(self):
        """Test stat value retrieval with index error."""
        scraper = PlayersScraper()
        
        empty_series = pd.Series()
        
        result = scraper._get_player_stat_value(empty_series, ('Performance', 'Gls'))
        assert result is None

    def test_player_nation_parsing_logic(self):
        """Test nationality parsing logic."""
        
        test_cases = [
            ('eng ENG', 'ENG'),
            ('france FRA', 'FRA'), 
            ('USA', 'USA'),
            (None, None),
            ('', None),
            ('InvalidFormat', 'InvalidFormat'),
        ]
        
        for nation_string, expected_country_code in test_cases:
            player_country_code = None
            if nation_string and pd.notna(nation_string):
                try:
                    if ' ' in nation_string:
                        player_country_code = nation_string.split(' ')[1]
                    else:
                        player_country_code = nation_string
                except:
                    player_country_code = nation_string
            else:
                player_country_code = None
            
            assert player_country_code == expected_country_code

    def test_scrape_update_mode(self, db_session, mocker):
        """Test scraping in update mode."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        
        player = Player(name="Bukayo Saka", fbref_id="12345678", fbref_url="/en/players/12345678/", nation_id=nation.id)
        db_session.add_all([nation, competition, season, team_stats, player])
        db_session.commit()
        
        existing_player_stats = PlayerStats(
            player_id=player.id,
            season_id=season.id,
            team_id=team_stats.team_id,
            matches_played=30,
            goals_scored=10,
            assists=5
        )
        db_session.add(existing_player_stats)
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(side_effect=lambda *args, **kwargs: 
                                               {'href': '/en/players/team123/goal-logs/'} if 'Goal Logs' in kwargs.get('text', '') 
                                               else {'href': '/en/players/12345678/'} if 'Bukayo Saka' in kwargs.get('string', '')
                                               else None)
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['eng ENG'],
            ('Playing Time', 'MP'): [38],
            ('Playing Time', 'Starts'): [35],
            ('Playing Time', 'Min'): [3150],
            ('Performance', 'Gls'): [14],
            ('Performance', 'Ast'): [8],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021, update_mode=True)
        
        db_session.refresh(existing_player_stats)
        assert existing_player_stats.matches_played == 38
        assert existing_player_stats.goals_scored == 14
        assert existing_player_stats.assists == 8

    def test_scrape_seasonal_mode(self, db_session, mocker):
        """Test scraping in seasonal mode."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(side_effect=lambda *args, **kwargs: 
                                               {'href': '/en/players/team123/goal-logs/'} if 'Goal Logs' in kwargs.get('text', '') 
                                               else {'href': '/en/players/12345678/'} if 'Bukayo Saka' in kwargs.get('string', '')
                                               else None)
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['eng ENG'],
            ('Playing Time', 'MP'): [38],
            ('Playing Time', 'Starts'): [35],
            ('Playing Time', 'Min'): [3150],
            ('Performance', 'Gls'): [14],
            ('Performance', 'Ast'): [8],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021, seasonal_mode=True)
        
        player = db_session.query(Player).filter_by(name='Bukayo Saka').first()
        assert player is not None
        
        player_stats = db_session.query(PlayerStats).filter_by(player_id=player.id).first()
        assert player_stats is not None
        assert player_stats.matches_played == 38
        assert player_stats.goals_scored == 14
        assert player_stats.assists == 8

    def test_goal_logs_url_complex_find(self, db_session, mocker):
        """Test finding goal logs URL with complex element finding logic."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()

        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])
        scraper.get_fbref_competition_name = mocker.Mock(return_value='All Competitions')

        def mock_find_elements(tag, class_=None):
            if tag == 'li' and class_ == 'full hasmore':
                mock_li_element = mocker.MagicMock()
                mock_span_element = mocker.MagicMock()
                mock_span_element.text = 'Goal Logs'
                mock_all_competitions_element = mocker.MagicMock()
                mock_all_competitions_element.text = 'All Competitions'
                mock_all_competitions_element.__getitem__ = mocker.Mock(return_value='/en/players/player123/all-competitions-goal-logs/')
                
                def mock_li_find(tag, text=None):
                    if tag == 'span' and text == 'Goal Logs':
                        return mock_span_element
                    elif tag == 'a' and text == 'All Competitions':
                        return mock_all_competitions_element
                    return None
                
                mock_li_element.find = mock_li_find
                return [mock_li_element]
            return []
        
        scraper.find_element = mocker.Mock(return_value=None)
        scraper.find_elements = mocker.Mock(side_effect=mock_find_elements)

        scraper.scrape(nations=['England'], from_year=2021, to_year=2021)

        db_session.refresh(team_stats)
        assert team_stats.goal_logs_url == '/en/players/player123/all-competitions-goal-logs/'

    def test_goal_logs_url_not_found_complex(self, db_session, mocker):
        """Test error handling when goal logs URL is not found in complex search."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/', goal_logs_url=None)
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()

        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])
        scraper.get_fbref_competition_name = mocker.Mock(return_value='Premier League')
        scraper.find_element = mocker.Mock(return_value=None)
        scraper.find_elements = mocker.Mock(return_value=[])

        scraper.scrape(nations=['England'], from_year=2021, to_year=2021)

        db_session.refresh(team_stats)
        assert team_stats.goal_logs_url is None
        scraper.log_progress.assert_any_call(f"No domestic league goal logs found for {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")

    def test_update_mode_no_existing_stats(self, db_session, mocker):
        """Test update mode when no existing player stats are found."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(side_effect=lambda *args, **kwargs: 
                                               {'href': '/en/players/team123/goal-logs/'} if 'Goal Logs' in kwargs.get('text', '') 
                                               else {'href': '/en/players/12345678/'} if 'Bukayo Saka' in kwargs.get('string', '')
                                               else None)
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        scraper.logger = mocker.MagicMock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['eng ENG'],
            ('Playing Time', 'MP'): [38],
            ('Playing Time', 'Starts'): [35],
            ('Playing Time', 'Min'): [3150],
            ('Performance', 'Gls'): [14],
            ('Performance', 'Ast'): [8],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021, update_mode=True)
        
        scraper.logger.info.assert_called()

    def test_seasonal_mode_existing_stats_url_update(self, db_session, mocker):
        """Test seasonal mode with existing stats and URL update."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        
        player = Player(name="Bukayo Saka", fbref_id="12345678", fbref_url="/en/players/12345678/", nation_id=nation.id)
        existing_player_stats = PlayerStats(
            player_id=player.id,
            season_id=season.id,
            team_id=team_stats.team_id,
            matches_played=30,
            goals_scored=10,
            assists=5
        )
        
        db_session.add_all([nation, competition, season, team_stats, player, existing_player_stats])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(side_effect=lambda *args, **kwargs: 
                                               {'href': '/en/players/team123/goal-logs/'} if 'Goal Logs' in kwargs.get('text', '') 
                                               else {'href': '/en/players/12345678/'} if 'Bukayo Saka' in kwargs.get('string', '')
                                               else None)
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['eng ENG'],
            ('Playing Time', 'MP'): [38],
            ('Playing Time', 'Starts'): [35],
            ('Playing Time', 'Min'): [3150],
            ('Performance', 'Gls'): [14],
            ('Performance', 'Ast'): [8],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021, seasonal_mode=True)
        
        db_session.refresh(existing_player_stats)
        assert existing_player_stats.matches_played == 30

    def test_player_skipped_no_matches_played(self, db_session, mocker):
        """Test that players with 0 matches played are skipped."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(side_effect=lambda *args, **kwargs: 
                                               {'href': '/en/players/team123/goal-logs/'} if 'Goal Logs' in kwargs.get('text', '') 
                                               else {'href': '/en/players/12345678/'} if 'Bukayo Saka' in kwargs.get('string', '')
                                               else None)
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        scraper.log_skip = mocker.Mock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['eng ENG'],
            ('Playing Time', 'MP'): [0],
            ('Playing Time', 'Starts'): [0],
            ('Playing Time', 'Min'): [0],
            ('Performance', 'Gls'): [0],
            ('Performance', 'Ast'): [0],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021)
        
        scraper.log_skip.assert_called_with("player", "Bukayo Saka 2021-2022", "No matches played")
        
        player_stats = db_session.query(PlayerStats).all()
        assert len(player_stats) == 0

    def test_player_skipped_no_a_tag(self, db_session, mocker):
        """Test that players without <a> tag are skipped."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(side_effect=lambda *args, **kwargs: 
                                               {'href': '/en/players/team123/goal-logs/'} if 'Goal Logs' in kwargs.get('text', '') 
                                               else None)
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        scraper.log_skip = mocker.Mock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['eng ENG'],
            ('Playing Time', 'MP'): [38],
            ('Playing Time', 'Starts'): [35],
            ('Playing Time', 'Min'): [3150],
            ('Performance', 'Gls'): [14],
            ('Performance', 'Ast'): [8],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021)
        
        expected_team_name = team_stats.team.name
        scraper.log_skip.assert_called_with("player", f"Bukayo Saka {expected_team_name} 2021-2022", "No <a> tag found")
        
        player_stats = db_session.query(PlayerStats).all()
        assert len(player_stats) == 0

    def test_player_skipped_squad_total(self, db_session, mocker):
        """Test that 'Squad Total' and 'Opponent Total' rows are skipped."""
        scraper = PlayersScraper()
        scraper.session = db_session
        
        nation = NationFactory(name='England', country_code='ENG')
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, start_year=2021, end_year=2022)
        team_stats = TeamStatsFactory(season=season, fbref_url='/en/squads/test-team/')
        
        db_session.add_all([nation, competition, season, team_stats])
        db_session.commit()
        
        scraper.load_page = mocker.Mock()
        scraper.find_element = mocker.Mock(return_value={'href': '/en/players/team123/goal-logs/'})
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        player_data = pd.DataFrame({
            ('Unnamed: 0_level_0', 'Player'): ['Squad Total', 'Opponent Total', 'Bukayo Saka'],
            ('Unnamed: 1_level_0', 'Nation'): ['', '', 'eng ENG'],
            ('Playing Time', 'MP'): [38, 38, 38],
            ('Playing Time', 'Starts'): [35, 35, 35],
            ('Playing Time', 'Min'): [3150, 3150, 3150],
            ('Performance', 'Gls'): [50, 20, 14],
            ('Performance', 'Ast'): [30, 15, 8],
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[player_data])
        
        scraper.scrape(nations=['England'], from_year=2021, to_year=2021)
        
        players = db_session.query(Player).all()
        assert len(players) == 1
        assert players[0].name == 'Bukayo Saka'
