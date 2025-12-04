"""Unit tests for NationsScraper."""

import pandas as pd
import pytest

from app.fbref_scraper.scrapers.nations_scraper import NationsScraper
from app.fbref_scraper.tests.utils.scraper_helpers import mock_fbref_countries_page
from app.models import Nation


class TestNationsScraper:
    """Test NationsScraper functionality."""

    def test_extract_fbref_id(self):
        """Test FBRef ID extraction from URL."""
        scraper = NationsScraper()

        test_cases = [
            ("/en/countries/ENG/", "ENG"),
            ("/en/countries/FRA/", "FRA"),
            ("/en/countries/GER/", "GER"),
        ]

        for url, expected_id in test_cases:
            result = scraper.extract_fbref_id(url)
            assert result == expected_id, f"Failed for URL: {url}"

    def test_fetch_page_success(self, mocker):
        """Test successful page fetching."""
        scraper = NationsScraper()

        mock_response = mocker.Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)

        soup = scraper.fetch_page("https://fbref.com/test")

        assert soup is not None
        assert soup.find("body").text == "Test content"
        scraper.http_session.get.assert_called_once()

    def test_fetch_page_http_error(self, mocker):
        """Test page fetching with HTTP error."""
        scraper = NationsScraper()

        mocker.patch.object(
            scraper.http_session, "get", side_effect=Exception("Connection timeout")
        )

        with pytest.raises(Exception, match="Connection timeout"):
            scraper.fetch_page("https://fbref.com/test")

    def test_fetch_html_table_success(self, mocker):
        """Test successful HTML table fetching."""
        scraper = NationsScraper()

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table><tr><td>Test</td></tr></table></body></html>"
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)

        mock_read_html = mocker.patch("pandas.read_html")
        mock_df = pd.DataFrame({"Country": ["England", "France"], "Governing Body": ["FA", "FFF"]})
        mock_read_html.return_value = [mock_df]

        result = scraper.fetch_html_table("https://fbref.com/en/countries/")

        assert len(result) == 1
        assert len(result[0]) == 2
        assert "England" in result[0]["Country"].values
        mock_read_html.assert_called_once()

    def test_fetch_html_table_error(self, mocker):
        """Test HTML table fetching with error."""
        scraper = NationsScraper()

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table></table></body></html>"
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)

        mock_read_html = mocker.patch("pandas.read_html")
        mock_read_html.side_effect = Exception("Table parsing failed")

        with pytest.raises(Exception, match="Table parsing failed"):
            scraper.fetch_html_table("https://fbref.com/test")

    def test_scrape_nations_success(self, mocker, db_session):
        """Test successful nations scraping."""
        scraper = NationsScraper()
        scraper.session = db_session

        mock_response = mocker.Mock()
        mock_response.text = mock_fbref_countries_page()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)

        mock_read_html = mocker.patch("pandas.read_html")
        mock_df = pd.DataFrame({"Country": ["England", "France"], "Governing Body": ["FA", "FFF"]})
        mock_read_html.return_value = [mock_df]

        scraper.scrape()

        nations = db_session.query(Nation).all()
        assert len(nations) == 2

        england = db_session.query(Nation).filter_by(name="England").first()
        assert england is not None
        assert england.country_code == "ENG"
        assert england.fbref_url == "/en/countries/ENG/"
        assert england.governing_body == "FA"
        assert england.clubs_url == "/en/countries/ENG/clubs/"

        france = db_session.query(Nation).filter_by(name="France").first()
        assert france is not None
        assert france.country_code == "FRA"
        assert france.fbref_url == "/en/countries/FRA/"

    def test_scrape_nations_duplicate_handling(self, mocker, db_session):
        """Test that duplicate nations are handled correctly."""
        scraper = NationsScraper()
        scraper.session = db_session

        existing_nation = Nation(
            name="Italy", country_code="ITA", fbref_url="/en/countries/ITA/", governing_body="FIGC"
        )
        db_session.add(existing_nation)
        db_session.commit()

        mock_response = mocker.Mock()
        mock_response.text = mock_fbref_countries_page()
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)

        mock_read_html = mocker.patch("pandas.read_html")
        mock_df = pd.DataFrame({"Country": ["Italy"], "Governing Body": ["FIGC"]})
        mock_read_html.return_value = [mock_df]

        scraper.scrape()

        italy_count = db_session.query(Nation).filter_by(name="Italy").count()
        assert italy_count == 1

        italy = db_session.query(Nation).filter_by(name="Italy").first()
        assert italy.id == existing_nation.id

    def test_log_skip_functionality(self):
        """Test logging skip functionality."""
        scraper = NationsScraper()

        scraper.log_skip("nation", "England", "Already exists")
        scraper.log_skip("nation", "France")

    def test_log_error_functionality(self, mocker):
        """Test logging error functionality."""
        scraper = NationsScraper()

        mocker.patch("app.fbref_scraper.core.scraper_config.is_debug_mode", return_value=False)

        test_exception = Exception("Test error")
        scraper.log_error("scraping", test_exception)

    def test_log_progress_functionality(self):
        """Test logging progress functionality."""
        scraper = NationsScraper()

        scraper.log_progress("Processing nations...")
