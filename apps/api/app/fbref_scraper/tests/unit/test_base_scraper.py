"""Unit tests for BaseScraper utility methods."""

import pytest
import requests

from app.fbref_scraper.core.base_scraper import BaseScraper, WebScraper
from app.models import Nation


class ConcreteBaseScraper(BaseScraper):
    """Concrete implementation of BaseScraper for testing."""

    def scrape(self, **kwargs):
        pass


class ConcreteWebScraper(WebScraper):
    """Concrete implementation of WebScraper for testing."""

    def scrape(self, **kwargs):
        pass


class TestBaseScraper:
    """Test BaseScraper functionality."""

    def test_extract_fbref_id(self):
        """Test FBRef ID extraction from various URL formats."""
        scraper = ConcreteBaseScraper()

        test_cases = [
            ("/en/countries/ENG/", "ENG"),
            ("/en/squads/18bb7c10/", "18bb7c10"),
            ("/en/players/12345678/", "12345678"),
            ("/en/matches/abcdefgh/", "abcdefgh"),
            ("/en/country/ARG/Argentina-Football", "ARG"),
            ("/en/comps/9/history/Premier-League-Sea:", "9"),
        ]

        for url, expected_id in test_cases:
            result = scraper.extract_fbref_id(url)
            assert result == expected_id, f"Failed for URL: {url}"

    def test_extract_fbref_id_edge_cases(self):
        """Test FBRef ID extraction edge cases."""
        scraper = ConcreteBaseScraper()

        assert scraper.extract_fbref_id("/en/countries/ENG") == "ENG"
        assert scraper.extract_fbref_id("/en/countries/ENG/clubs/") == "ENG"
        assert scraper.extract_fbref_id("/en/countries/ENG/clubs/teams/") == "ENG"

    def test_log_skip_default_reason(self):
        """Test log_skip with default reason."""
        scraper = ConcreteBaseScraper()
        scraper.log_skip("nation", "England")

    def test_log_skip_custom_reason(self):
        """Test log_skip with custom reason."""
        scraper = ConcreteBaseScraper()
        scraper.log_skip("nation", "England", "Custom reason")

    def test_log_error(self, mocker):
        """Test log_error functionality."""
        scraper = ConcreteBaseScraper()
        test_exception = Exception("Test error")
        mocker.patch("app.fbref_scraper.core.scraper_config.is_debug_mode", return_value=False)
        scraper.log_error("scraping", test_exception)

    def test_log_progress(self):
        """Test log_progress functionality."""
        scraper = ConcreteBaseScraper()
        scraper.log_progress("Processing data...")


class TestWebScraper:
    """Test WebScraper functionality."""

    def test_initialization(self):
        """Test WebScraper initialization."""
        scraper = ConcreteWebScraper()

        assert scraper.soup is None
        assert scraper.config is not None
        assert scraper.logger is not None

    def test_load_page_success(self, mocker):
        """Test successful page loading."""
        scraper = ConcreteWebScraper()

        mock_fetch = mocker.patch.object(scraper, "fetch_page")
        mock_soup = mocker.Mock()
        mock_fetch.return_value = mock_soup

        result = scraper.load_page("https://fbref.com/test")

        assert result == mock_soup
        assert scraper.soup == mock_soup
        mock_fetch.assert_called_once_with("https://fbref.com/test", None)

    def test_load_page_with_sleep_time(self, mocker):
        """Test page loading with custom sleep time."""
        scraper = ConcreteWebScraper()

        mock_fetch = mocker.patch.object(scraper, "fetch_page")
        mock_soup = mocker.Mock()
        mock_fetch.return_value = mock_soup

        result = scraper.load_page("https://fbref.com/test", sleep_time=10)

        assert result == mock_soup
        mock_fetch.assert_called_once_with("https://fbref.com/test", 10)

    def test_find_element_no_page_loaded(self):
        """Test find_element when no page is loaded."""
        scraper = ConcreteWebScraper()

        with pytest.raises(ValueError, match="No page loaded"):
            scraper.find_element("div")

    def test_find_element_success(self, mocker):
        """Test successful element finding."""
        scraper = ConcreteWebScraper()

        mock_soup = mocker.Mock()
        mock_element = mocker.Mock()
        mock_soup.find.return_value = mock_element
        scraper.soup = mock_soup

        result = scraper.find_element("div", class_="test")

        assert result == mock_element
        mock_soup.find.assert_called_once_with("div", class_="test")

    def test_find_elements_no_page_loaded(self):
        """Test find_elements when no page is loaded."""
        scraper = ConcreteWebScraper()

        with pytest.raises(ValueError, match="No page loaded"):
            scraper.find_elements("div")

    def test_find_elements_with_attributes(self, mocker):
        """Test find_elements with attributes parameter."""
        scraper = ConcreteWebScraper()

        mock_soup = mocker.Mock()
        mock_elements = [mocker.Mock(), mocker.Mock()]
        mock_soup.find_all.return_value = mock_elements
        scraper.soup = mock_soup

        attributes = {"class": "test"}
        result = scraper.find_elements("div", attributes)

        assert result == mock_elements
        mock_soup.find_all.assert_called_once_with("div", attributes)

    def test_find_elements_with_kwargs(self, mocker):
        """Test find_elements with kwargs."""
        scraper = ConcreteWebScraper()

        mock_soup = mocker.Mock()
        mock_elements = [mocker.Mock()]
        mock_soup.find_all.return_value = mock_elements
        scraper.soup = mock_soup

        result = scraper.find_elements("div", class_="test", id="example")

        assert result == mock_elements
        mock_soup.find_all.assert_called_once_with("div", class_="test", id="example")

    def test_find_elements_no_attributes_or_kwargs(self, mocker):
        """Test find_elements with no attributes or kwargs."""
        scraper = ConcreteWebScraper()

        mock_soup = mocker.Mock()
        mock_elements = [mocker.Mock()]
        mock_soup.find_all.return_value = mock_elements
        scraper.soup = mock_soup

        result = scraper.find_elements("div")

        assert result == mock_elements
        mock_soup.find_all.assert_called_once_with("div")

    def test_find_or_create_record_new_record(self, db_session, mocker):
        """Test find_or_create_record creating new record."""
        scraper = ConcreteWebScraper()
        scraper.session = db_session

        nation_data = {
            "name": "Test Nation",
            "country_code": "TST",
            "fbref_url": "/en/countries/TST/",
            "governing_body": "Test FA",
        }

        mock_log_skip = mocker.patch.object(scraper, "log_skip")
        result = scraper.find_or_create_record(
            Nation, {"name": "Test Nation"}, nation_data, "nation: Test Nation"
        )

        assert result.name == "Test Nation"
        assert result.country_code == "TST"
        mock_log_skip.assert_not_called()

    def test_find_or_create_record_existing_record(self, db_session, mocker):
        """Test find_or_create_record finding existing record."""
        scraper = ConcreteWebScraper()
        scraper.session = db_session

        existing_nation = Nation(
            name="Existing Nation",
            country_code="EXT",
            fbref_url="/en/countries/EXT/",
            governing_body="Existing FA",
        )
        db_session.add(existing_nation)
        db_session.commit()

        nation_data = {
            "name": "Existing Nation",
            "country_code": "EXT",
            "fbref_url": "/en/countries/EXT/",
            "governing_body": "Existing FA",
        }

        mock_log_skip = mocker.patch.object(scraper, "log_skip")
        result = scraper.find_or_create_record(
            Nation, {"name": "Existing Nation"}, nation_data, "nation: Existing Nation"
        )

        assert result.id == existing_nation.id
        assert result.name == "Existing Nation"
        mock_log_skip.assert_called_once()

    def test_fetch_html_table_success(self, mocker):
        """Test successful HTML table fetching."""
        scraper = ConcreteWebScraper()

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table><tr><td>Test</td></tr></table></body></html>"
        mock_response.raise_for_status = mocker.Mock()

        mock_df = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)
        mocker.patch("pandas.read_html", return_value=[mock_df])
        mocker.patch("time.sleep")

        result = scraper.fetch_html_table("https://fbref.com/test")

        assert len(result) == 1
        assert result[0] == mock_df

    def test_fetch_html_table_http_error(self, mocker):
        """Test HTML table fetching with HTTP error."""
        scraper = ConcreteWebScraper()

        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "404 Client Error: Not Found"
        )
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)
        mocker.patch("time.sleep")

        with pytest.raises(requests.HTTPError):
            scraper.fetch_html_table("https://fbref.com/test")

    def test_fetch_html_table_with_sleep_time(self, mocker):
        """Test HTML table fetching with custom sleep time."""
        scraper = ConcreteWebScraper()

        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table><tr><td>Test</td></tr></table></body></html>"
        mock_response.raise_for_status = mocker.Mock()

        mock_sleep = mocker.patch("time.sleep")
        mock_df = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)
        mocker.patch("pandas.read_html", return_value=[mock_df])

        result = scraper.fetch_html_table("https://fbref.com/test", sleep_time=5)

        assert len(result) == 1
        mock_sleep.assert_called_once_with(5)

    def test_fetch_page_success(self, mocker):
        """Test successful page fetching."""
        scraper = ConcreteBaseScraper()

        mock_response = mocker.Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)
        mocker.patch("time.sleep")

        result = scraper.fetch_page("https://fbref.com/test")

        assert result is not None
        assert result.find("body").text == "Test content"
        scraper.http_session.get.assert_called_once()

    def test_fetch_page_with_sleep_time(self, mocker):
        """Test page fetching with custom sleep time."""
        scraper = ConcreteBaseScraper()

        mock_response = mocker.Mock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.status_code = 200
        mock_response.raise_for_status = mocker.Mock()
        mocker.patch.object(scraper.http_session, "get", return_value=mock_response)

        mock_sleep = mocker.patch("time.sleep")

        result = scraper.fetch_page("https://fbref.com/test", sleep_time=3)

        assert result is not None
        mock_sleep.assert_called_once_with(3)

    def test_log_error_and_continue(self, mocker):
        """Test log_error_and_continue functionality."""
        scraper = ConcreteBaseScraper()
        test_exception = Exception("Test error")

        mock_logger = mocker.patch.object(scraper, "logger")
        mocker.patch("app.fbref_scraper.core.scraper_config.is_debug_mode", return_value=False)

        scraper.log_error_and_continue("scraping", test_exception, "test_entity")

        mock_logger.error.assert_called_once()

    def test_save_and_load_progress(self, mocker):
        """Test progress saving and loading."""
        scraper = ConcreteBaseScraper()

        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mocker.patch("json.dump")

        mocker.patch.object(scraper, "load_progress", return_value={"test": "data"})

        progress_data = {"test": "data"}
        scraper.save_progress(progress_data)

        result = scraper.load_progress()
        assert result == {"test": "data"}

    def test_clear_progress(self, mocker):
        """Test progress clearing."""
        scraper = ConcreteBaseScraper()

        mock_remove = mocker.patch("os.remove")
        mocker.patch("os.path.exists", return_value=True)

        scraper.clear_progress()

        mock_remove.assert_called_once()

    def test_log_failed_record_and_get_failed_records(self, mocker):
        """Test failed record logging and retrieval."""
        scraper = ConcreteBaseScraper()

        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mocker.patch("os.path.exists", return_value=True)

        scraper.log_failed_record("Player", "player_123", "Test error")

        mock_open.return_value.readlines.return_value = ["Player:player_123:Test error\n"]
        result = scraper.get_failed_records()

        assert len(result) == 1
        assert "Player:player_123:Test error" in result[0]

    def test_run_method(self, mocker):
        """Test run method calls scrape."""
        scraper = ConcreteBaseScraper()

        mock_scrape = mocker.patch.object(scraper, "scrape")

        scraper.run(test_param="value")

        mock_scrape.assert_called_once_with(test_param="value")
