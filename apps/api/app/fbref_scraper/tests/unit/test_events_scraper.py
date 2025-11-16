"""Tests for EventsScraper."""

from datetime import date

from app.fbref_scraper.scrapers.events_scraper import EventsScraper
from app.tests.utils.factories import (
    CompetitionFactory,
    MatchFactory,
    NationFactory,
    PlayerFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)

class TestEventsScraper:
    """Test cases for EventsScraper."""

    @staticmethod
    def _create_event_data_mock_find(mocker, venue, minute, score_before_event):
        """Helper to create mock_find for event data parsing tests."""
        def mock_find(_tag, attrs):
            if attrs == {'data-stat': 'venue'}:
                element = mocker.Mock()
                element.text.strip.return_value = venue
                return element
            elif attrs == {'data-stat': 'minute'}:
                element = mocker.Mock()
                element.text.strip.return_value = minute
                return element
            elif attrs == {'data-stat': 'score_before_event'}:
                element = mocker.Mock()
                element.text.strip.return_value = score_before_event
                return element
            return None
        return mock_find

    def test_scrape_success(self, mocker, db_session):
        """Test successful events scraping."""
        scraper = EventsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition)
        team = TeamFactory(nation=nation)
        team_stats = TeamStatsFactory(team=team, season=season, goal_logs_url="/en/squads/team_123/goal-logs/")

        db_session.add_all([nation, competition, season, team, team_stats])
        db_session.commit()

        mocker.patch('app.fbref_scraper.core.get_config').return_value = mocker.Mock(FBREF_BASE_URL="https://fbref.com")

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_event = mocker.Mock()
        mock_event.find.side_effect = lambda _tag, attrs: self._create_mock_element(_tag, attrs, mocker)

        scraper.soup.select.return_value = [mocker.Mock(), mock_event]

        mock_match = MatchFactory()
        mock_scorer_element = mocker.Mock()
        mock_scorer_element.text = "Test Player"
        mock_scorer_element.find.return_value = mocker.Mock()
        mock_scorer_element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/players/player_123/")

        mock_player = PlayerFactory()
        scraper._extract_match_and_player = mocker.Mock(return_value=(mock_match, mock_scorer_element, mock_player))

        scraper.find_or_create_record = mocker.Mock()

        scraper.scrape(nations=["England"])

        scraper.load_page.assert_called()
        assert scraper.find_or_create_record.call_count >= 1

    def test_scrape_with_year_filtering(self, mocker, db_session):
        """Test events scraping with date filtering."""
        scraper = EventsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(nation=nation)
        season_2022 = SeasonFactory(competition=competition, start_year=2022)
        season_2023 = SeasonFactory(competition=competition, start_year=2023)
        team = TeamFactory(nation=nation)

        team_stats_2022 = TeamStatsFactory(team=team, season=season_2022, goal_logs_url="/en/squads/team_123/goal-logs/")
        team_stats_2023 = TeamStatsFactory(team=team, season=season_2023, goal_logs_url="/en/squads/team_456/goal-logs/")

        db_session.add_all([nation, competition, season_2022, season_2023, team, team_stats_2022, team_stats_2023])
        db_session.commit()

        mocker.patch('app.fbref_scraper.core.get_config').return_value = mocker.Mock(FBREF_BASE_URL="https://fbref.com")
        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.soup.select.return_value = []
        scraper.find_or_create_record = mocker.Mock()

        scraper.scrape(nations=["England"], from_date=date(2023, 1, 1), to_date=date(2023, 12, 31))

        assert scraper.load_page.call_count >= 1

    def test_parse_event_data_home_venue(self, mocker):
        """Test event data parsing for home venue."""
        scraper = EventsScraper()
        mock_event = mocker.Mock()
        mock_event.find.side_effect = self._create_event_data_mock_find(mocker, "Home", "45", "2-1")

        result = scraper._parse_event_data(mock_event)

        assert result['minute'] == 45
        assert result['home_goals_pre_event'] == 2
        assert result['away_goals_pre_event'] == 1
        assert result['home_goals_post_event'] == 3
        assert result['away_goals_post_event'] == 1

    def test_parse_event_data_away_venue(self, mocker):
        """Test event data parsing for away venue."""
        scraper = EventsScraper()
        mock_event = mocker.Mock()
        mock_event.find.side_effect = self._create_event_data_mock_find(mocker, "Away", "67", "1-2")

        result = scraper._parse_event_data(mock_event)

        assert result['minute'] == 67
        assert result['home_goals_pre_event'] == 2
        assert result['away_goals_pre_event'] == 1
        assert result['home_goals_post_event'] == 2
        assert result['away_goals_post_event'] == 2

    def test_parse_event_data_extra_time(self, mocker):
        """Test event data parsing with extra time."""
        scraper = EventsScraper()
        mock_event = mocker.Mock()
        mock_event.find.side_effect = self._create_event_data_mock_find(mocker, "Home", "90+3", "1-1")

        result = scraper._parse_event_data(mock_event)

        assert result['minute'] == 93

    def test_parse_event_data_empty_score(self, mocker):
        """Test event data parsing with empty score."""
        scraper = EventsScraper()
        mock_event = mocker.Mock()
        mock_event.find.side_effect = self._create_event_data_mock_find(mocker, "Home", "1", "")

        result = scraper._parse_event_data(mock_event)

        assert result['minute'] == 1
        assert result['home_goals_pre_event'] is None
        assert result['away_goals_pre_event'] is None
        assert result['home_goals_post_event'] is None
        assert result['away_goals_post_event'] is None

    def test_scrape_goal_with_xg(self, mocker, db_session):
        """Test goal scraping with xG data."""
        scraper = EventsScraper()
        scraper.session = db_session

        mock_event = mocker.Mock()
        mock_scorer_element = mocker.Mock()
        mock_scorer_element.text.strip.return_value = "Test Player"
        
        mock_match = MatchFactory()
        scoring_player_id = 123

        def mock_find(_tag, attrs):
            if attrs == {'data-stat': 'xg_shot'}:
                element = mocker.Mock()
                element.text.strip.return_value = "0.8"
                return element
            elif attrs == {'data-stat': 'psxg_shot'}:
                element = mocker.Mock()
                element.text.strip.return_value = "0.9"
                return element
            return None

        mock_event.find.side_effect = mock_find

        scraper._parse_event_data = mocker.Mock(return_value={
            'minute': 45,
            'home_goals_pre_event': 1,
            'away_goals_pre_event': 0,
            'home_goals_post_event': 2,
            'away_goals_post_event': 0,
        })

        scraper.find_or_create_record = mocker.Mock()

        scraper._scrape_goal(mock_event, mock_scorer_element, mock_match, scoring_player_id)

        scraper.find_or_create_record.assert_called_once()
        call_args = scraper.find_or_create_record.call_args
        goal_dict = call_args[0][2]
        
        assert goal_dict['event_type'] == 'goal'
        assert goal_dict['xg'] == 0.8
        assert goal_dict['post_shot_xg'] == 0.9
        assert abs(goal_dict['xg_difference'] - 0.1) < 0.0001

    def test_scrape_goal_own_goal(self, mocker, db_session):
        """Test goal scraping for own goal."""
        scraper = EventsScraper()
        scraper.session = db_session

        mock_event = mocker.Mock()
        mock_scorer_element = mocker.Mock()
        mock_scorer_element.text.strip.return_value = "Test Player (OG)"
        
        mock_match = MatchFactory()
        scoring_player_id = 123

        mock_event.find = mocker.Mock(return_value=None)

        scraper._parse_event_data = mocker.Mock(return_value={
            'minute': 30,
            'home_goals_pre_event': 0,
            'away_goals_pre_event': 1,
            'home_goals_post_event': 1,
            'away_goals_post_event': 1,
        })

        scraper.find_or_create_record = mocker.Mock()

        scraper._scrape_goal(mock_event, mock_scorer_element, mock_match, scoring_player_id)

        call_args = scraper.find_or_create_record.call_args
        goal_dict = call_args[0][2]
        
        assert goal_dict['event_type'] == 'own goal'

    def test_scrape_assist(self, mocker, db_session):
        """Test assist scraping."""
        scraper = EventsScraper()
        scraper.session = db_session

        mock_event = mocker.Mock()
        mock_match = MatchFactory()
        assisting_player_id = 456

        scraper._parse_event_data = mocker.Mock(return_value={
            'minute': 60,
            'home_goals_pre_event': 1,
            'away_goals_pre_event': 1,
            'home_goals_post_event': 2,
            'away_goals_post_event': 1,
        })

        scraper.find_or_create_record = mocker.Mock()

        scraper._scrape_assist(mock_event, mock_match, assisting_player_id)

        call_args = scraper.find_or_create_record.call_args
        assist_dict = call_args[0][2]
        
        assert assist_dict['event_type'] == 'assist'
        assert assist_dict['xg'] is None
        assert assist_dict['post_shot_xg'] is None
        assert assist_dict['xg_difference'] is None

    def test_extract_match_and_player_existing_player(self, mocker, db_session):
        """Test match and player extraction with existing player."""
        scraper = EventsScraper()
        scraper.session = db_session

        player = PlayerFactory(fbref_id="player_123")
        match = MatchFactory(fbref_id="match_456")
        db_session.add_all([player, match])
        db_session.commit()

        mock_event = mocker.Mock()
        
        def mock_find(_tag, attrs):
            if attrs == {'data-stat': 'date'}:
                element = mocker.Mock()
                element.find.return_value = mocker.Mock()
                element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/matches/match_456/")
                return element
            elif attrs == {'data-stat': 'scorer'}:
                element = mocker.Mock()
                element.text = "Test Player"
                element.find.return_value = mocker.Mock()
                element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/players/player_123/")
                return element
            return None

        mock_event.find.side_effect = mock_find

        result_match, result_scorer_element, result_player = scraper._extract_match_and_player(mock_event)

        assert result_match.id == match.id
        assert result_player.id == player.id
        assert result_scorer_element.text == "Test Player"

    def test_extract_match_and_player_create_player(self, mocker, db_session):
        """Test match and player extraction with player creation."""
        scraper = EventsScraper()
        scraper.session = db_session

        match = MatchFactory(fbref_id="match_456")
        db_session.commit()

        mock_event = mocker.Mock()
        
        def mock_find(_tag, attrs):
            if attrs == {'data-stat': 'date'}:
                element = mocker.Mock()
                element.find.return_value = mocker.Mock()
                element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/matches/match_456/")
                return element
            elif attrs == {'data-stat': 'scorer'}:
                element = mocker.Mock()
                element.text = "New Player"
                element.find.return_value = mocker.Mock()
                element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/players/player_789/")
                return element
            return None

        mock_event.find.side_effect = mock_find

        new_player = PlayerFactory(fbref_id="player_789")
        scraper.find_or_create_record = mocker.Mock(return_value=new_player)
        
        def mock_query(model_class):
            mock_query_obj = mocker.Mock()
            if model_class.__name__ == 'Match':
                mock_query_obj.filter.return_value.first.return_value = match
            elif model_class.__name__ == 'Player':
                mock_query_obj.filter.return_value.first.return_value = None
            return mock_query_obj
        
        scraper.session.query = mock_query

        result_match, result_scorer_element, result_player = scraper._extract_match_and_player(mock_event)

        assert result_match.id == match.id
        assert result_player.id == new_player.id
        assert result_scorer_element.text == "New Player"
        
        scraper.find_or_create_record.assert_called_once()

    def test_scrape_handles_no_events_found(self, mocker, db_session):
        """Test scraping when no events are found."""
        scraper = EventsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition)
        team = TeamFactory(nation=nation)
        team_stats = TeamStatsFactory(team=team, season=season, goal_logs_url="/en/squads/team_123/goal-logs/")
        
        db_session.add_all([nation, competition, season, team, team_stats])
        db_session.commit()

        mocker.patch('app.fbref_scraper.core.get_config').return_value = mocker.Mock(FBREF_BASE_URL="https://fbref.com")
        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.soup.select.return_value = []
        scraper.find_or_create_record = mocker.Mock()

        scraper.scrape(nations=["England"])

        scraper.find_or_create_record.assert_not_called()

    def test_scrape_handles_competition_filtering(self, mocker, db_session):
        """Test scraping with competition filtering."""
        scraper = EventsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition)
        team = TeamFactory(nation=nation)
        team_stats = TeamStatsFactory(team=team, season=season, goal_logs_url="/en/squads/team_123/goal-logs/")
        
        db_session.add_all([nation, competition, season, team, team_stats])
        db_session.commit()

        mocker.patch('app.fbref_scraper.core.get_config').return_value = mocker.Mock(FBREF_BASE_URL="https://fbref.com")
        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_event = mocker.Mock()
        
        def mock_find(_tag, attrs):
            if attrs == {'data-stat': 'comp'}:
                element = mocker.Mock()
                element.text = "Premier League"
                element.strip.return_value = "Premier League"
                return element
            elif attrs == {'data-stat': 'venue'}:
                element = mocker.Mock()
                element.text = "Home"
                element.strip.return_value = "Home"
                return element
            elif attrs == {'data-stat': 'minute'}:
                element = mocker.Mock()
                element.text = "45"
                element.strip.return_value = "45"
                return element
            elif attrs == {'data-stat': 'score_before_event'}:
                element = mocker.Mock()
                element.text = "1-0"
                element.strip.return_value = "1-0"
                return element
            elif attrs == {'data-stat': 'assist'}:
                element = mocker.Mock()
                element.text = ""
                element.strip.return_value = ""
                return element
            elif attrs == {'data-stat': 'scorer'}:
                element = mocker.Mock()
                element.text = "Test Player"
                element.strip.return_value = "Test Player"
                element.find.return_value = mocker.Mock()
                element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/players/player_123/")
                return element
            elif attrs == {'data-stat': 'date'}:
                element = mocker.Mock()
                element.find.return_value = mocker.Mock()
                element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/matches/match_123/")
                return element
            return None

        mock_event.find.side_effect = mock_find
        
        scraper.soup.select.return_value = [mocker.Mock(), mock_event]

        mock_match = MatchFactory()
        mock_scorer_element = mocker.Mock()
        mock_scorer_element.text = "Test Player"
        mock_scorer_element.find.return_value = mocker.Mock()
        mock_scorer_element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/players/player_123/")
        
        mock_player = PlayerFactory()
        scraper._extract_match_and_player = mocker.Mock(return_value=(mock_match, mock_scorer_element, mock_player))

        scraper.find_or_create_record = mocker.Mock()

        scraper.scrape(nations=["England"])

        scraper.find_or_create_record.assert_called()

    def test_scrape_skips_non_major_competitions(self, mocker, db_session):
        """Test scraping skips non-major competitions."""
        scraper = EventsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition)
        team = TeamFactory(nation=nation)
        team_stats = TeamStatsFactory(team=team, season=season, goal_logs_url="/en/squads/team_123/goal-logs/")
        
        db_session.add_all([nation, competition, season, team, team_stats])
        db_session.commit()

        mocker.patch('app.fbref_scraper.core.get_config').return_value = mocker.Mock(FBREF_BASE_URL="https://fbref.com")
        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_event = mocker.Mock()
        
        def mock_find(_tag, attrs):
            if attrs == {'data-stat': 'comp'}:
                element = mocker.Mock()
                element.text.strip.return_value = "Championship"
                return element
            return None

        mock_event.find.side_effect = mock_find
        
        scraper.soup.select.return_value = [mocker.Mock(), mock_event]

        scraper.find_or_create_record = mocker.Mock()

        scraper.scrape(nations=["England"])

        scraper.find_or_create_record.assert_not_called()

    def _create_mock_element(self, _tag, attrs, mocker):
        """Helper method to create mock elements for testing."""
        element = mocker.Mock()
        element.text = "Test Text"
        element.strip = mocker.Mock(return_value="Test Text")
        element.find.return_value = mocker.Mock()
        element.find.return_value.__getitem__ = mocker.Mock(return_value="/test/url/")
        
        if attrs == {'data-stat': 'comp'}:
            element.text = "Premier League"
            element.strip.return_value = "Premier League"
        elif attrs == {'data-stat': 'venue'}:
            element.text = "Home"
            element.strip.return_value = "Home"
        elif attrs == {'data-stat': 'minute'}:
            element.text = "45"
            element.strip.return_value = "45"
        elif attrs == {'data-stat': 'score_before_event'}:
            element.text = "1-0"
            element.strip.return_value = "1-0"
        elif attrs == {'data-stat': 'scorer'}:
            element.text = "Test Player"
            element.strip.return_value = "Test Player"
            element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/players/player_123/")
        elif attrs == {'data-stat': 'assist'}:
            element.text = ""
            element.strip.return_value = ""
        elif attrs == {'data-stat': 'xg_shot'}:
            element.text = "0.8"
            element.strip.return_value = "0.8"
        elif attrs == {'data-stat': 'psxg_shot'}:
            element.text = "0.9"
            element.strip.return_value = "0.9"
        elif attrs == {'data-stat': 'date'}:
            element.find.return_value.__getitem__ = mocker.Mock(return_value="/en/matches/match_123/")
            
        return element
