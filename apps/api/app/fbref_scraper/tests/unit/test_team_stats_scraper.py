"""Unit tests for TeamStatsScraper."""

import pandas as pd

from app.fbref_scraper.scrapers.team_stats_scraper import TeamStatsScraper
from app.models import Team, TeamStats
from app.tests.utils.factories import (
    CompetitionFactory,
    NationFactory,
    SeasonFactory,
)


class TestTeamStatsScraper:
    """Test TeamStatsScraper functionality."""

    def test_extract_fbref_id(self):
        """Test FBRef ID extraction from URL."""
        scraper = TeamStatsScraper()

        test_cases = [
            ("/en/squads/18bb7c10/Arsenal-Stats", "18bb7c10"),
            ("/en/squads/19538871/Manchester-United-Stats", "19538871"),
            ("/en/squads/206d90db/Chelsea-Stats", "206d90db"),
        ]

        for url, expected_id in test_cases:
            result = scraper.extract_fbref_id(url)
            assert result == expected_id, f"Failed for URL: {url}"

    def test_scrape_success_league_competition(self, mocker, db_session):
        """Test successful team stats scraping for league competition."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1, 2],
                "Squad": ["Arsenal", "Chelsea"],
                "MP": [38, 38],
                "W": [28, 25],
                "D": [5, 8],
                "L": [5, 5],
                "GF": [91, 76],
                "GA": [29, 33],
                "GD": [62, 43],
                "Pts": [89, 83],
                "Pts/MP": [2.34, 2.18],
                "xG": [85.2, 78.1],
                "xGA": [31.5, 35.2],
                "xGD": [53.7, 42.9],
                "xGD/90": [1.41, 1.13],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/comps/9/2023-2024/schedule/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats"
                )
                return mock_link
            elif "Chelsea" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/206d90db/Chelsea-Stats"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape()

        teams = db_session.query(Team).all()
        assert len(teams) == 2

        team_stats = db_session.query(TeamStats).all()
        assert len(team_stats) == 2

        arsenal_stats = (
            db_session.query(TeamStats).join(Team).filter(Team.name == "Arsenal").first()
        )
        assert arsenal_stats is not None
        assert arsenal_stats.matches_played == 38
        assert arsenal_stats.wins == 28
        assert arsenal_stats.points == 89
        assert arsenal_stats.goal_difference == 62

    def test_scrape_skips_cup_competition(self, mocker, db_session):
        """Test that cup competitions are skipped."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(name="FA Cup", competition_type="Cup", nation=nation)
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch("time.sleep")

        scraper.scrape()

        team_stats = db_session.query(TeamStats).all()
        assert len(team_stats) == 0

    def test_scrape_handles_nan_rankings(self, mocker, db_session):
        """Test that NaN rankings are skipped."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1, float("nan"), 3],
                "Squad": ["Arsenal", "Invalid Team", "Chelsea"],
                "MP": [38, 38, 38],
                "W": [28, 25, 25],
                "D": [5, 8, 8],
                "L": [5, 5, 5],
                "GF": [91, 76, 76],
                "GA": [29, 33, 33],
                "GD": [62, 43, 43],
                "Pts": [89, 83, 83],
                "Pts/MP": [2.34, 2.18, 2.18],
                "xG": [85.2, 78.1, 78.1],
                "xGA": [31.5, 35.2, 35.2],
                "xGD": [53.7, 42.9, 42.9],
                "xGD/90": [1.41, 1.13, 1.13],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        scraper.find_element = mocker.Mock(return_value=None)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats"
                )
                return mock_link
            elif "Chelsea" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/206d90db/Chelsea-Stats"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape()

        team_stats = db_session.query(TeamStats).all()
        assert len(team_stats) == 2

    def test_scrape_handles_missing_team_links(self, mocker, db_session):
        """Test handling when team links are not found."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1],
                "Squad": ["Unknown Team"],
                "MP": [38],
                "W": [28],
                "D": [5],
                "L": [5],
                "GF": [91],
                "GA": [29],
                "GD": [62],
                "Pts": [89],
                "Pts/MP": [2.34],
                "xG": [85.2],
                "xGA": [31.5],
                "xGD": [53.7],
                "xGD/90": [1.41],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.find_element = mocker.Mock(return_value=None)
        scraper.soup.select_one = mocker.Mock(return_value=None)

        scraper.scrape()

        team_stats = db_session.query(TeamStats).all()
        assert len(team_stats) == 0

    def test_scrape_handles_no_team_stats_found(self, mocker, db_session):
        """Test handling when no team stats are found in HTML table."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch("app.fbref_scraper.core.get_year_range", return_value=(2020, 2030))

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.find_element = mocker.Mock(return_value=None)

        scraper.fetch_html_table = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()

        scraper.scrape(nations=["England"])

        team_stats = db_session.query(TeamStats).all()
        assert len(team_stats) == 0
        scraper.log_progress.assert_any_call("No team stats found for Premier League 2023-2024")

    def test_scrape_with_country_filtering(self, mocker, db_session):
        """Test scraping with country code filtering."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        england = NationFactory(name="England", country_code="ENG")
        france = NationFactory(name="France", country_code="FRA")

        eng_competition = CompetitionFactory(name="Premier League", nation=england)
        fra_competition = CompetitionFactory(name="Ligue 1", nation=france)

        eng_season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=eng_competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        fra_season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=fra_competition,
            fbref_url="/en/comps/13/2023-2024/",
        )

        db_session.add_all(
            [england, france, eng_competition, fra_competition, eng_season, fra_season]
        )
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        def mock_read_html(url):
            if "comps/9" in url:
                return [
                    pd.DataFrame(
                        {
                            "Rk": [1],
                            "Squad": ["Arsenal"],
                            "MP": [38],
                            "W": [28],
                            "D": [5],
                            "L": [5],
                            "GF": [91],
                            "GA": [29],
                            "GD": [62],
                            "Pts": [89],
                            "Pts/MP": [2.34],
                            "xG": [85.2],
                            "xGA": [31.5],
                            "xGD": [53.7],
                            "xGD/90": [1.41],
                        }
                    )
                ]
            else:
                return [
                    pd.DataFrame(
                        {
                            "Rk": [1],
                            "Squad": ["PSG"],
                            "MP": [38],
                            "W": [28],
                            "D": [5],
                            "L": [5],
                            "GF": [91],
                            "GA": [29],
                            "GD": [62],
                            "Pts": [89],
                            "Pts/MP": [2.34],
                            "xG": [85.2],
                            "xGA": [31.5],
                            "xGD": [53.7],
                            "xGD/90": [1.41],
                        }
                    )
                ]

        scraper.fetch_html_table = mocker.Mock(side_effect=mock_read_html)

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/comps/9/2023-2024/schedule/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape(nations=["England"])

        team_stats = db_session.query(TeamStats).all()
        assert len(team_stats) == 1

        team = db_session.query(Team).first()
        assert team.name == "Arsenal"

    def test_scrape_duplicate_handling(self, mocker, db_session):
        """Test that duplicate team stats are handled correctly."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        team = Team(name="Arsenal", fbref_id="18bb7c10", nation_id=nation.id)
        db_session.add_all([nation, competition, season, team])
        db_session.commit()

        existing_stats = TeamStats(
            team_id=team.id,
            season_id=season.id,
            fbref_url="/en/squads/18bb7c10/Arsenal-Stats",
            matches_played=38,
            wins=28,
            points=89,
        )
        db_session.add(existing_stats)
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1],
                "Squad": ["Arsenal"],
                "MP": [38],
                "W": [28],
                "D": [5],
                "L": [5],
                "GF": [91],
                "GA": [29],
                "GD": [62],
                "Pts": [89],
                "Pts/MP": [2.34],
                "xG": [85.2],
                "xGA": [31.5],
                "xGD": [53.7],
                "xGD/90": [1.41],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.find_element = mocker.Mock(return_value=None)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape()

        team_stats_count = db_session.query(TeamStats).count()
        assert team_stats_count == 1

        stats = db_session.query(TeamStats).first()
        assert stats.id == existing_stats.id

    def test_log_progress_functionality(self):
        """Test logging progress functionality."""
        scraper = TeamStatsScraper()

        scraper.log_progress("Processing team stats...")
        scraper.log_progress("Team stats processing complete")

    def test_log_error_functionality(self, mocker):
        """Test logging error functionality."""
        scraper = TeamStatsScraper()

        mocker.patch("app.fbref_scraper.core.scraper_config.is_debug_mode", return_value=False)

        test_exception = Exception("Test scraping error")
        scraper.log_error("scraping", test_exception)

    def test_scrape_update_mode(self, mocker, db_session):
        """Test scraping in update mode."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        team = Team(name="Arsenal", fbref_id="18bb7c10", nation_id=nation.id)

        db_session.add_all([nation, competition, season, team])
        db_session.commit()

        existing_team_stats = TeamStats(
            team_id=team.id,
            season_id=season.id,
            fbref_url="/en/squads/18bb7c10/Arsenal-Stats",
            matches_played=30,
            wins=20,
            points=65,
        )

        db_session.add(existing_team_stats)
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1],
                "Squad": ["Arsenal"],
                "MP": [38],
                "W": [28],
                "D": [5],
                "L": [5],
                "GF": [91],
                "GA": [29],
                "GD": [62],
                "Pts": [89],
                "Pts/MP": [2.34],
                "xG": [85.2],
                "xGA": [31.5],
                "xGD": [53.7],
                "xGD/90": [1.41],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/comps/9/2023-2024/schedule/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape(update_mode=True)

        db_session.refresh(existing_team_stats)
        assert existing_team_stats.matches_played == 38
        assert existing_team_stats.wins == 28
        assert existing_team_stats.points == 89

    def test_scrape_seasonal_mode_existing_stats(self, mocker, db_session):
        """Test seasonal mode with existing team stats."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        team = Team(name="Arsenal", fbref_id="18bb7c10", nation_id=nation.id)

        db_session.add_all([nation, competition, season, team])
        db_session.commit()

        existing_team_stats = TeamStats(
            team_id=team.id,
            season_id=season.id,
            fbref_url="/en/squads/18bb7c10/Arsenal-Stats",
            matches_played=30,
            wins=20,
            points=65,
        )

        db_session.add(existing_team_stats)
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1],
                "Squad": ["Arsenal"],
                "MP": [38],
                "W": [28],
                "D": [5],
                "L": [5],
                "GF": [91],
                "GA": [29],
                "GD": [62],
                "Pts": [89],
                "Pts/MP": [2.34],
                "xG": [85.2],
                "xGA": [31.5],
                "xGD": [53.7],
                "xGD/90": [1.41],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/comps/9/2023-2024/schedule/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats-Updated"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape(seasonal_mode=True)

        db_session.refresh(existing_team_stats)
        assert existing_team_stats.fbref_url == "/en/squads/18bb7c10/Arsenal-Stats-Updated"

    def test_scrape_seasonal_mode_new_stats(self, mocker, db_session):
        """Test seasonal mode with new team stats creation."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        team = Team(name="Arsenal", fbref_id="18bb7c10", nation_id=nation.id)

        db_session.add_all([nation, competition, season, team])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1],
                "Squad": ["Arsenal"],
                "MP": [38],
                "W": [28],
                "D": [5],
                "L": [5],
                "GF": [91],
                "GA": [29],
                "GD": [62],
                "Pts": [89],
                "Pts/MP": [2.34],
                "xG": [85.2],
                "xGA": [31.5],
                "xGD": [53.7],
                "xGD/90": [1.41],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/comps/9/2023-2024/schedule/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape(seasonal_mode=True)

        team_stats = db_session.query(TeamStats).all()
        assert len(team_stats) == 1
        assert team_stats[0].matches_played == 38
        assert team_stats[0].wins == 28
        assert team_stats[0].points == 89

    def test_scrape_update_mode_no_existing_stats(self, mocker, db_session):
        """Test update mode when no existing team stats are found."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        team = Team(name="Arsenal", fbref_id="18bb7c10", nation_id=nation.id)

        db_session.add_all([nation, competition, season, team])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.logger = mocker.Mock()

        mock_df = pd.DataFrame(
            {
                "Rk": [1],
                "Squad": ["Arsenal"],
                "MP": [38],
                "W": [28],
                "D": [5],
                "L": [5],
                "GF": [91],
                "GA": [29],
                "GD": [62],
                "Pts": [89],
                "Pts/MP": [2.34],
                "xG": [85.2],
                "xGA": [31.5],
                "xGD": [53.7],
                "xGD/90": [1.41],
            }
        )
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/comps/9/2023-2024/schedule/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        def mock_select_one(selector):
            if "Arsenal" in selector:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(
                    return_value="/en/squads/18bb7c10/Arsenal-Stats"
                )
                return mock_link
            return None

        scraper.soup.select_one = mocker.Mock(side_effect=mock_select_one)

        scraper.scrape(update_mode=True)

        scraper.logger.warning.assert_called()

    def test_scrape_matches_url_handling(self, mocker, db_session):
        """Test matches URL handling and updates."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )

        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/comps/9/2023-2024/schedule/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        scraper.scrape()

        db_session.refresh(season)
        assert season.matches_url == "/en/comps/9/2023-2024/schedule/"

    def test_scrape_matches_url_none_when_not_found(self, mocker, db_session):
        """Test that matches URL is set to None when not found."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )

        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])

        scraper.find_element = mocker.Mock(return_value=None)

        scraper.scrape()

        db_session.refresh(season)
        assert season.matches_url is None

    def test_scrape_matches_url_skips_generic_url(self, mocker, db_session):
        """Test that generic matches URL is skipped."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )

        db_session.add_all([nation, competition, season])
        db_session.commit()

        mocker.patch("requests.get").return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock(),
        )
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        scraper.load_page = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])

        def mock_find_element(_tag, string):
            if string == "Scores & Fixtures":
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value="/en/matches/")
                return mock_link
            return None

        scraper.find_element = mocker.Mock(side_effect=mock_find_element)

        scraper.scrape()

        db_session.refresh(season)
        assert season.matches_url is None

    def test_scrape_error_handling_and_continue(self, mocker, db_session):
        """Test error handling during season processing."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season1 = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        season2 = SeasonFactory(
            start_year=2022,
            end_year=2023,
            competition=competition,
            fbref_url="/en/comps/9/2022-2023/",
        )

        db_session.add_all([nation, competition, season1, season2])
        db_session.commit()

        mocker.patch.object(scraper.http_session, "get", side_effect=Exception("Network error"))
        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch("app.fbref_scraper.core.get_year_range", return_value=(2020, 2030))

        scraper.log_error_and_continue = mocker.Mock()

        scraper.scrape(nations=["England"])

        scraper.log_error_and_continue.assert_called()

    def test_scrape_progress_resumption(self, mocker, db_session):
        """Test progress resumption functionality."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season1 = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )
        season2 = SeasonFactory(
            start_year=2022,
            end_year=2023,
            competition=competition,
            fbref_url="/en/comps/9/2022-2023/",
        )

        db_session.add_all([nation, competition, season1, season2])
        db_session.commit()

        scraper.load_progress = mocker.Mock(return_value={"last_processed_index": 0})
        scraper.save_progress = mocker.Mock()
        scraper.clear_progress = mocker.Mock()
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])

        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch("app.fbref_scraper.core.get_year_range", return_value=(2020, 2030))

        scraper.scrape(nations=["England"])

        scraper.log_progress.assert_any_call("Resuming from index 1")
        assert scraper.load_page.call_count == 1

    def test_scrape_clears_progress_on_completion(self, mocker, db_session):
        """Test that progress is cleared when scraping completes successfully."""
        scraper = TeamStatsScraper()
        scraper.session = db_session

        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League", competition_type="League", nation=nation
        )
        season = SeasonFactory(
            start_year=2023,
            end_year=2024,
            competition=competition,
            fbref_url="/en/comps/9/2023-2024/",
        )

        db_session.add_all([nation, competition, season])
        db_session.commit()

        scraper.load_progress = mocker.Mock(return_value=None)
        scraper.save_progress = mocker.Mock()
        scraper.clear_progress = mocker.Mock()
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.soup = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])

        mocker.patch("app.fbref_scraper.core.get_config").return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch("app.fbref_scraper.core.get_year_range", return_value=(2020, 2030))

        scraper.scrape(nations=["England"])

        scraper.clear_progress.assert_called_once()
        scraper.log_progress.assert_any_call("Team stats scraping completed successfully")
