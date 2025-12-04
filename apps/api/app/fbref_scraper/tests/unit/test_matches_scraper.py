"""Unit tests for MatchesScraper."""

from datetime import date

from app.fbref_scraper.scrapers.matches_scraper import MatchesScraper
from app.models import Competition, Match, Nation, Season
from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)


class TestMatchesScraper:
    """Test MatchesScraper functionality."""

    @staticmethod
    def _create_mock_find_with_tag(mock_find_data_stat):
        """Helper to create mock_find_with_tag function."""

        def mock_find_with_tag(**kwargs):
            data_stat = kwargs.get("data-stat")
            return mock_find_data_stat(data_stat)

        return mock_find_with_tag

    @staticmethod
    def _setup_mock_config(mocker):
        """Helper to setup mock config with FBREF_BASE_URL."""
        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )
        return mock_config

    @staticmethod
    def _setup_scraper_mocks(scraper, mocker):
        """Helper to setup common scraper method mocks."""
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()

    def test_scrape_success(self, db_session, mocker):
        """Test successful match scraping."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(name="Premier League", fbref_id="9", nation=nation)
        season = SeasonFactory(
            competition=competition, matches_url="/en/comps/9/2021-2022/schedule/"
        )

        home_team = TeamFactory(name="Arsenal")
        away_team = TeamFactory(name="Chelsea")

        home_team_stats = TeamStatsFactory(team=home_team, fbref_url="/en/squads/18bb7c10/")
        away_team_stats = TeamStatsFactory(team=away_team, fbref_url="/en/squads/cfd3cf68/")

        db_session.add_all(
            [nation, competition, season, home_team, away_team, home_team_stats, away_team_stats]
        )
        db_session.commit()

        mock_tr = mocker.MagicMock()
        mock_score_td = mocker.MagicMock()
        mock_match_link = mocker.MagicMock()
        mock_match_link.__getitem__ = mocker.Mock(
            side_effect=lambda key: "/en/matches/c0fb79cf/" if key == "href" else None
        )
        mock_score_td.find.return_value = mock_match_link
        mock_score_td.text = "2–1"

        mock_date_td = mocker.MagicMock()
        mock_date_td.text.strip.return_value = "2021-08-14"

        mock_home_td = mocker.MagicMock()
        mock_home_td.a.__getitem__ = mocker.Mock(
            side_effect=lambda key: "/en/squads/18bb7c10/" if key == "href" else None
        )

        mock_away_td = mocker.MagicMock()
        mock_away_td.a.__getitem__ = mocker.Mock(
            side_effect=lambda key: "/en/squads/cfd3cf68/" if key == "href" else None
        )

        def mock_find_data_stat(value):
            if value == "score":
                return mock_score_td
            elif value == "date":
                return mock_date_td
            elif value == "home_team":
                return mock_home_td
            elif value == "away_team":
                return mock_away_td
            return None

        def mock_find_with_tag(*args, **kwargs):
            data_stat = None

            if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], dict):
                data_stat = args[1].get("data-stat")
            elif len(args) >= 1 and isinstance(args[0], dict):
                data_stat = args[0].get("data-stat")
            elif "attrs" in kwargs:
                data_stat = (
                    kwargs["attrs"].get("data-stat") if isinstance(kwargs["attrs"], dict) else None
                )

            return mock_find_data_stat(data_stat)

        mock_tr.find.side_effect = mock_find_with_tag

        scraper.soup = mocker.MagicMock()

        def mock_select(*args, **kwargs):
            return [mocker.MagicMock(), mock_tr]

        scraper.soup.select = mock_select
        self._setup_scraper_mocks(scraper, mocker)
        scraper.extract_fbref_id = mocker.Mock(return_value="c0fb79cf")

        self._setup_mock_config(mocker)

        scraper.scrape()

        matches = db_session.query(Match).all()
        assert len(matches) >= 1
        match = matches[0]
        assert match.home_team_goals == 2
        assert match.away_team_goals == 1
        assert match.date == date(2021, 8, 14)
        assert match.fbref_id == "c0fb79cf"
        assert match.home_team_id == home_team.id
        assert match.away_team_id == away_team.id
        assert match.season_id == season.id

    def test_scrape_with_country_filter(self, db_session, mocker):
        """Test scraping with country code filter."""
        scraper = MatchesScraper()
        scraper.session = db_session

        england_nation = NationFactory(name="England", country_code="ENG")
        france_nation = NationFactory(name="France", country_code="FRA")
        db_session.commit()

        england_comp = CompetitionFactory(
            name="Premier League",
            fbref_id="9",
            fbref_url="/en/comps/9/Premier-League/",
            nation=england_nation,
        )
        france_comp = CompetitionFactory(
            name="Ligue 1", fbref_id="13", fbref_url="/en/comps/13/Ligue-1/", nation=france_nation
        )
        db_session.commit()

        england_season = SeasonFactory(
            competition=england_comp, matches_url="/en/comps/9/2021-2022/schedule/"
        )
        SeasonFactory(competition=france_comp, matches_url="/en/comps/13/2021-2022/schedule/")
        db_session.commit()

        self._setup_scraper_mocks(scraper, mocker)
        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = []

        self._setup_mock_config(mocker)

        scraper.scrape(nations=["England"])

        england_season = (
            db_session.query(Season)
            .join(Competition)
            .join(Nation)
            .filter(Nation.country_code == "ENG")
            .first()
        )
        expected_message = f"Processing matches for Premier League {england_season.start_year}-{england_season.end_year}"
        scraper.log_progress.assert_any_call(expected_message)

    def test_scrape_skips_playoff_matches(self, db_session, mocker):
        """Test that playoff matches are skipped."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory()
        competition = CompetitionFactory()
        season = SeasonFactory(
            competition=competition, matches_url="/en/comps/9/2021-2022/schedule/"
        )
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mock_tr = mocker.MagicMock()
        mock_score_td = mocker.MagicMock()
        mock_score_td.a.__getitem__ = mocker.Mock(return_value="/en/matches/play-off-match/")
        mock_tr.find.return_value = mock_score_td

        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = [mocker.MagicMock(), mock_tr]
        self._setup_scraper_mocks(scraper, mocker)
        self._setup_mock_config(mocker)

        scraper.scrape()

        matches = db_session.query(Match).all()
        assert len(matches) == 0

    def test_scrape_skips_matches_without_score(self, db_session, mocker):
        """Test that matches without score data are skipped."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory()
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition, matches_url="/schedule/")
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mock_tr = mocker.MagicMock()
        mock_tr.find.return_value = None

        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = [mocker.MagicMock(), mock_tr]
        self._setup_scraper_mocks(scraper, mocker)
        self._setup_mock_config(mocker)

        scraper.scrape()

        matches = db_session.query(Match).all()
        assert len(matches) == 0

    def test_scrape_skips_invalid_score_format(self, db_session, mocker):
        """Test that matches with invalid score format are skipped."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory()
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition, matches_url="/schedule/")
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mock_tr = mocker.MagicMock()
        mock_score_td = mocker.MagicMock()
        mock_score_td.a.__getitem__ = mocker.Mock(return_value="/en/matches/match-id/")
        mock_score_td.text = "Invalid Score Format"
        mock_tr.find.return_value = mock_score_td

        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = [mocker.MagicMock(), mock_tr]
        self._setup_scraper_mocks(scraper, mocker)
        self._setup_mock_config(mocker)

        scraper.scrape()

        matches = db_session.query(Match).all()
        assert len(matches) == 0

    def test_scrape_skips_matches_without_teams(self, db_session, mocker):
        """Test that matches where teams are not found are skipped."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory()
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition, matches_url="/schedule/")
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mock_tr = mocker.MagicMock()
        mock_score_td = mocker.MagicMock()
        mock_score_td.a.__getitem__ = mocker.Mock(return_value="/en/matches/match-id/")
        mock_score_td.text = "2–1"

        mock_date_td = mocker.MagicMock()
        mock_date_td.text.strip.return_value = "2021-08-14"

        mock_home_td = mocker.MagicMock()
        mock_home_td.a.__getitem__ = mocker.Mock(return_value="/en/squads/nonexistent/")

        mock_away_td = mocker.MagicMock()
        mock_away_td.a.__getitem__ = mocker.Mock(return_value="/en/squads/nonexistent2/")

        def mock_find_data_stat(value):
            if value == "score":
                return mock_score_td
            elif value == "date":
                return mock_date_td
            elif value == "home_team":
                return mock_home_td
            elif value == "away_team":
                return mock_away_td
            return None

        mock_tr.find.side_effect = self._create_mock_find_with_tag(mock_find_data_stat)

        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = [mocker.MagicMock(), mock_tr]
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.extract_fbref_id = mocker.Mock(return_value="match-id")

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape()

        matches = db_session.query(Match).all()
        assert len(matches) == 0

    def test_extract_fbref_id_from_match_url(self, db_session, mocker):
        """Test FBRef ID extraction from match URL."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory()
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition, matches_url="/schedule/")
        db_session.add_all([nation, competition, season])
        db_session.commit()

        scraper.extract_fbref_id = mocker.Mock(return_value="abc123def")
        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = []
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape()

        scraper.extract_fbref_id.assert_not_called()

    def test_date_parsing_from_match_row(self, db_session, mocker):
        """Test date parsing from match row data."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory()
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition, matches_url="/schedule/")
        db_session.add_all([nation, competition, season])
        db_session.commit()

        test_date = "2021-12-25"

        mock_tr = mocker.MagicMock()
        mock_score_td = mocker.MagicMock()
        mock_score_td.a.__getitem__ = mocker.Mock(return_value="/en/matches/match-id/")
        mock_score_td.text = "1–0"

        mock_date_td = mocker.MagicMock()
        mock_date_td.text.strip.return_value = test_date

        def mock_find_data_stat(value):
            if value == "score":
                return mock_score_td
            elif value == "date":
                return mock_date_td
            return None

        mock_tr.find.side_effect = self._create_mock_find_with_tag(mock_find_data_stat)

        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = [mocker.MagicMock(), mock_tr]
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.extract_fbref_id = mocker.Mock(return_value="match-id")

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape()

        matches = db_session.query(Match).all()
        assert len(matches) == 0

    def test_scrape_with_date_filtering(self, db_session, mocker):
        """Test scraping with date range filtering."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, matches_url="/schedule/")

        home_team1 = TeamFactory(name="Arsenal", nation=nation)
        away_team1 = TeamFactory(name="Chelsea", nation=nation)
        home_team2 = TeamFactory(name="Liverpool", nation=nation)
        away_team2 = TeamFactory(name="Manchester City", nation=nation)

        home_team_stats1 = TeamStatsFactory(
            team=home_team1, season=season, fbref_url="/en/squads/18bb7c10/stats/"
        )
        away_team_stats1 = TeamStatsFactory(
            team=away_team1, season=season, fbref_url="/en/squads/cfd3cf68/stats/"
        )
        home_team_stats2 = TeamStatsFactory(
            team=home_team2, season=season, fbref_url="/en/squads/822bd0ba/stats/"
        )
        away_team_stats2 = TeamStatsFactory(
            team=away_team2, season=season, fbref_url="/en/squads/b8fd03ef/stats/"
        )

        db_session.add_all(
            [
                nation,
                competition,
                season,
                home_team1,
                away_team1,
                home_team2,
                away_team2,
                home_team_stats1,
                away_team_stats1,
                home_team_stats2,
                away_team_stats2,
            ]
        )
        db_session.commit()

        mock_match_in_range = mocker.Mock()
        mock_match_out_of_range = mocker.Mock()

        def mock_find_element_in_range(tag, attrs):
            if attrs == {"data-stat": "score"}:
                element = mocker.Mock()
                mock_match_link = mocker.Mock()
                mock_match_link.__getitem__ = mocker.Mock(
                    side_effect=lambda key: "/en/matches/match1/" if key == "href" else None
                )
                element.find.return_value = mock_match_link
                element.text = "2–1"
                return element
            elif attrs == {"data-stat": "date"}:
                element = mocker.Mock()
                element.text.strip.return_value = "2021-08-14"
                return element
            elif attrs == {"data-stat": "home_team"}:
                element = mocker.Mock()
                element.a.__getitem__ = mocker.Mock(
                    side_effect=lambda key: "/en/squads/18bb7c10/stats/" if key == "href" else None
                )
                return element
            elif attrs == {"data-stat": "away_team"}:
                element = mocker.Mock()
                element.a.__getitem__ = mocker.Mock(
                    side_effect=lambda key: "/en/squads/cfd3cf68/stats/" if key == "href" else None
                )
                return element
            return None

        def mock_find_element_out_of_range(tag, attrs):
            if attrs == {"data-stat": "score"}:
                element = mocker.Mock()
                mock_match_link = mocker.Mock()
                mock_match_link.__getitem__ = mocker.Mock(
                    side_effect=lambda key: "/en/matches/match2/" if key == "href" else None
                )
                element.find.return_value = mock_match_link
                element.text = "1–0"
                return element
            elif attrs == {"data-stat": "date"}:
                element = mocker.Mock()
                element.text.strip.return_value = "2021-07-01"
                return element
            elif attrs == {"data-stat": "home_team"}:
                element = mocker.Mock()
                element.a.__getitem__ = mocker.Mock(
                    side_effect=lambda key: "/en/squads/822bd0ba/stats/" if key == "href" else None
                )
                return element
            elif attrs == {"data-stat": "away_team"}:
                element = mocker.Mock()
                element.a.__getitem__ = mocker.Mock(
                    side_effect=lambda key: "/en/squads/b8fd03ef/stats/" if key == "href" else None
                )
                return element
            return None

        mock_match_in_range.find.side_effect = mock_find_element_in_range
        mock_match_out_of_range.find.side_effect = mock_find_element_out_of_range

        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = [
            mocker.MagicMock(),
            mock_match_in_range,
            mock_match_out_of_range,
        ]
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.extract_fbref_id = mocker.Mock(
            side_effect=lambda x: "match1" if "match1" in x else "match2"
        )

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape(nations=["England"], from_date=date(2021, 8, 1), to_date=date(2021, 8, 31))

        matches = db_session.query(Match).all()
        assert len(matches) == 1
        assert matches[0].date == date(2021, 8, 14)
        assert matches[0].home_team_id == home_team1.id
        assert matches[0].away_team_id == away_team1.id

    def test_scrape_progress_resumption(self, db_session, mocker):
        """Test progress resumption functionality."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition1 = CompetitionFactory(name="Premier League", nation=nation)
        competition2 = CompetitionFactory(name="Championship", nation=nation)

        season1 = SeasonFactory(competition=competition1, matches_url="/schedule1/")
        season2 = SeasonFactory(competition=competition2, matches_url="/schedule2/")

        db_session.add_all([nation, competition1, competition2, season1, season2])
        db_session.commit()

        scraper.load_progress = mocker.Mock(return_value={"last_processed_index": 0})
        scraper.save_progress = mocker.Mock()
        scraper.clear_progress = mocker.Mock()
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = []

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape(nations=["England"])

        scraper.log_progress.assert_any_call("Resuming from index 1")
        assert scraper.load_page.call_count == 1

    def test_scrape_skips_season_without_matches_url(self, db_session, mocker):
        """Test that seasons without matches URL are skipped."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(nation=nation)
        season = SeasonFactory(competition=competition, matches_url=None)

        db_session.add_all([nation, competition, season])
        db_session.commit()

        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.log_skip = mocker.Mock()

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape(nations=["England"])

        scraper.log_skip.assert_called_with(
            "season",
            f"{season.competition.name} {season.start_year}-{season.end_year}",
            "No matches URL available",
        )
        scraper.load_page.assert_not_called()

    def test_scrape_error_handling_and_continue(self, db_session, mocker):
        """Test error handling during season processing."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition1 = CompetitionFactory(name="Premier League", nation=nation)
        competition2 = CompetitionFactory(name="Championship", nation=nation)

        season1 = SeasonFactory(competition=competition1, matches_url="/schedule1/")
        season2 = SeasonFactory(competition=competition2, matches_url="/schedule2/")

        db_session.add_all([nation, competition1, competition2, season1, season2])
        db_session.commit()

        scraper.load_page = mocker.Mock(side_effect=Exception("Network error"))
        scraper.log_progress = mocker.Mock()
        scraper.log_error_and_continue = mocker.Mock()

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape(nations=["England"])

        scraper.log_error_and_continue.assert_called()
        assert scraper.load_page.call_count == 2

    def test_scrape_clears_progress_on_completion(self, db_session, mocker):
        """Test that progress is cleared when scraping completes successfully."""
        scraper = MatchesScraper()
        scraper.session = db_session

        nation = NationFactory()
        competition = CompetitionFactory()
        season = SeasonFactory(competition=competition, matches_url="/schedule/")

        db_session.add_all([nation, competition, season])
        db_session.commit()

        scraper.load_progress = mocker.Mock(return_value=None)
        scraper.save_progress = mocker.Mock()
        scraper.clear_progress = mocker.Mock()
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.soup = mocker.MagicMock()
        scraper.soup.select.return_value = []

        mock_config = mocker.Mock()
        mock_config.FBREF_BASE_URL = "https://fbref.com"
        mocker.patch(
            "app.fbref_scraper.scrapers.matches_scraper.get_config", return_value=mock_config
        )

        scraper.scrape()

        scraper.clear_progress.assert_called_once()
        scraper.log_progress.assert_any_call("Matches scraping completed successfully")
