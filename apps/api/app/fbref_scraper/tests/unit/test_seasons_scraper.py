"""Unit tests for SeasonsScraper."""

import pandas as pd
import pytest

from scrapers.seasons_scraper import SeasonsScraper
from models import Season
from tests.utils.factories import CompetitionFactory, NationFactory


class TestSeasonsScraper:
    """Test SeasonsScraper functionality."""

    def test_extract_fbref_id(self, db_session):
        """Test FBRef ID extraction from URL."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        test_cases = [
            ("/en/comps/9/history/Premier-League-Seasons", "9"),
            ("/en/comps/20/serie-a/Serie-A-Seasons", "20"),
            ("/en/comps/31/bundesliga/1-Bundesliga-Seasons", "31")
        ]
        
        for url, expected_id in test_cases:
            result = scraper.extract_fbref_id(url)
            assert result == expected_id, f"Failed for URL: {url}"

    def test_scrape_success(self, mocker, db_session):
        """Test successful seasons scraping."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        mock_df = pd.DataFrame({
            'Season': ['2023-2024', '2022-2023'],
            'Champion': ['Chelsea', 'Arsenal']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        mocker.patch('core.get_year_range', return_value=(2020, 2030))
        
        def mock_find_element(tag, string):
            if string in ['2023-2024', '2022-2023']:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/comps/9/{string}/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"])

        seasons = db_session.query(Season).all()
        assert len(seasons) == 2

        season_2023 = db_session.query(Season).filter_by(start_year=2023).first()
        assert season_2023 is not None
        assert season_2023.start_year == 2023
        assert season_2023.end_year == 2024
        assert season_2023.competition_id == competition.id
        assert season_2023.fbref_url == "/en/comps/9/2023-2024/"

    def test_year_range_filtering(self, mocker, db_session):
        """Test that seasons outside the year range are filtered out."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        mock_df = pd.DataFrame({
            'Season': ['2018-2019', '2022-2023', '2024-2025'],
            'Champion': ['City', 'Arsenal', 'Chelsea']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        mocker.patch('core.get_year_range', return_value=(2020, 2030))
        
        def mock_find_element(tag, string):
            if string in ['2022-2023', '2024-2025']:  
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/comps/9/{string}/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"])

        seasons = db_session.query(Season).all()
        assert len(seasons) == 2

        season_years = [season.start_year for season in seasons]
        assert 2018 not in season_years
        assert 2022 in season_years
        assert 2024 in season_years

    def test_single_year_seasons(self, mocker, db_session):
        """Test parsing of single year seasons (e.g., "2020")."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        mock_df = pd.DataFrame({
            'Season': ['2020', '2022-2023'],
            'Champion': ['Liverpool', 'City']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        mocker.patch('core.get_year_range', return_value=(2015, 2030))
        
        def mock_find_element(tag, string):
            if string in ['2020', '2022-2023']:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/comps/9/{string}/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"])
        
        seasons = db_session.query(Season).order_by(Season.start_year).all()
        assert len(seasons) == 2

        season_2020 = seasons[0]
        assert season_2020.start_year == 2020
        assert season_2020.end_year == 2020
        
        season_2022 = seasons[1]
        assert season_2022.start_year == 2022
        assert season_2022.end_year == 2023

    def test_duplicate_handling(self, mocker, db_session):
        """Test that duplicate seasons are handled correctly."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        
        existing_season = Season(
            start_year=2022,
            end_year=2023,
            fbref_url="/en/comps/9/2022-2023/",
            competition_id=competition.id
        )
        db_session.add(existing_season)
        db_session.commit()
        
        mock_df = pd.DataFrame({
            'Season': ['2022-2023', '2023-2024'],
            'Champion': ['Arsenal', 'Chelsea']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        mocker.patch('core.get_year_range', return_value=(2020, 2030))
        
        def mock_find_element(tag, string):
            if string in ['2022-2023', '2023-2024']:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/comps/9/{string}/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"])
        
        seasons_count = db_session.query(Season).count()
        assert seasons_count == 2
        
        season_2023 = db_session.query(Season).filter_by(start_year=2023).first()
        assert season_2023 is not None
        assert season_2023.id != existing_season.id

    def test_no_seasons_found(self, mocker, db_session):
        """Test handling when no seasons are found in HTML table."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        
        mocker.patch('pandas.read_html', return_value=[])
        mocker.patch('core.get_year_range', return_value=(2020, 2030))
        
        scraper.scrape(nations=["England"])
        
        seasons_count = db_session.query(Season).count()
        assert seasons_count == 0

    def test_log_progress_functionality(self, db_session):
        """Test logging progress functionality."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        scraper.log_progress("Processing seasons...")
        scraper.log_progress("Season processing complete")

    def test_log_skip_functionality(self, db_session):
        """Test logging skip functionality."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        scraper.log_skip("season", "2022-2023", "Out of year range")
        scraper.log_skip("season", "Duplicate season")

    def test_log_error_functionality(self, mocker, db_session):
        """Test logging error functionality."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        mocker.patch('core.base_scraper.is_debug_mode', return_value=False)
        
        test_exception = Exception("Test scraping error")
        scraper.log_error("scraping", test_exception)

    def test_scrape_seasonal_mode_existing_season(self, mocker, db_session):
        """Test seasonal mode with existing season."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        
        existing_season = Season(
            start_year=2022,
            end_year=2023,
            fbref_url="/en/comps/9/2022-2023/",
            competition_id=competition.id
        )
        
        db_session.add_all([nation, competition, existing_season])
        db_session.commit()

        scraper.load_page = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])
        scraper.log_progress = mocker.Mock()
        
        scraper.scrape(nations=["England"], seasonal_mode=True)
        
        seasons_count = db_session.query(Season).count()
        assert seasons_count == 1
        assert existing_season.id == db_session.query(Season).first().id

    def test_scrape_seasonal_mode_url_update(self, mocker, db_session):
        """Test seasonal mode with URL update for archived season."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        
        existing_season = Season(
            start_year=2022,
            end_year=2023,
            fbref_url="/en/comps/9/2022-2023/",
            competition=competition
        )
        
        db_session.add_all([nation, competition, existing_season])
        db_session.commit()

        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.logger = mocker.Mock()
        scraper.log_skip = mocker.Mock()
        
        mock_df = pd.DataFrame({
            'Season': ['2022-2023'],
            'Champion': ['Arsenal']
        })
        scraper.fetch_html_table = mocker.Mock(return_value=[mock_df])
        
        def mock_find_element(tag, string):
            if string == '2022-2023':
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value='/en/comps/9/2022-2023/archived/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"], seasonal_mode=True)
        
        db_session.refresh(existing_season)
        assert existing_season.fbref_url == '/en/comps/9/2022-2023/archived/'
        scraper.logger.info.assert_any_call("Updated season URL to archived format: 2022-2023 for Premier League")

    def test_scrape_seasonal_mode_new_season(self, mocker, db_session):
        """Test seasonal mode with new season creation."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        mock_df = pd.DataFrame({
            'Season': ['2023-2024'],
            'Champion': ['Chelsea']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        mocker.patch('core.get_year_range', return_value=(2020, 2030))
        
        def mock_find_element(tag, string):
            if string == '2023-2024':
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value='/en/comps/9/2023-2024/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"], seasonal_mode=True)
        
        seasons_count = db_session.query(Season).count()
        assert seasons_count == 1
        
        new_season = db_session.query(Season).first()
        assert new_season.start_year == 2023
        assert new_season.end_year == 2024
        assert new_season.fbref_url == '/en/comps/9/2023-2024/'

    def test_scrape_error_handling_and_continue(self, mocker, db_session):
        """Test error handling during competition processing."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition1 = CompetitionFactory(name="Premier League", nation=nation)
        competition2 = CompetitionFactory(name="Championship", nation=nation)
        
        db_session.add_all([nation, competition1, competition2])
        db_session.commit()

        scraper.load_page = mocker.Mock(side_effect=Exception("Network error"))
        
        with pytest.raises(Exception, match="Network error"):
            scraper.scrape(nations=["England"])

    def test_scrape_with_year_range_parameters(self, mocker, db_session):
        """Test scraping with custom year range parameters."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        mock_df = pd.DataFrame({
            'Season': ['2018-2019', '2022-2023', '2024-2025'],
            'Champion': ['City', 'Arsenal', 'Chelsea']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        
        def mock_find_element(tag, string):
            if string in ['2022-2023', '2024-2025']:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/comps/9/{string}/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"], from_year=2022, to_year=2024)

        seasons = db_session.query(Season).all()
        assert len(seasons) == 2
        
        season_years = [season.start_year for season in seasons]
        assert 2018 not in season_years
        assert 2022 in season_years
        assert 2024 in season_years

    def test_scrape_skips_season_without_link(self, mocker, db_session):
        """Test that seasons without links are skipped."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        mock_df = pd.DataFrame({
            'Season': ['2022-2023'],
            'Champion': ['Arsenal']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        mocker.patch('core.get_year_range', return_value=(2020, 2030))
        
        scraper.find_element = mocker.Mock(return_value=None)
        
        scraper.scrape(nations=["England"])
        
        seasons_count = db_session.query(Season).count()
        assert seasons_count == 0

    def test_scrape_handles_single_year_season_edge_cases(self, mocker, db_session):
        """Test handling of edge cases in single year season parsing."""
        scraper = SeasonsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code="ENG")
        competition = CompetitionFactory(
            name="Premier League",
            fbref_url="/en/comps/9/",
            nation=nation
        )
        
        db_session.add_all([nation, competition])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )

        mock_df = pd.DataFrame({
            'Season': ['2020', '2021-2022'],
            'Champion': ['Liverpool', 'City']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        mocker.patch('core.get_year_range', return_value=(2015, 2030))
        
        def mock_find_element(tag, string):
            if string in ['2020', '2021-2022']:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/comps/9/{string}/')
                return mock_link
            return None
        
        scraper.find_element = mocker.Mock(side_effect=mock_find_element)
        
        scraper.scrape(nations=["England"])
        
        seasons = db_session.query(Season).order_by(Season.start_year).all()
        assert len(seasons) == 2
        
        season_2020 = seasons[0]
        assert season_2020.start_year == 2020
        assert season_2020.end_year == 2020
        
        season_2021 = seasons[1]
        assert season_2021.start_year == 2021
        assert season_2021.end_year == 2022
