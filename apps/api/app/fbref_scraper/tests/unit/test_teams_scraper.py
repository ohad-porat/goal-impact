"""Unit tests for TeamsScraper."""

import pandas as pd

from scrapers.teams_scraper import TeamsScraper
from models import Team
from tests.utils.factories import NationFactory


class TestTeamsScraper:
    """Test TeamsScraper functionality."""


    def test_extract_fbref_id(self, db_session):
        """Test FBRef ID extraction from URL."""
        scraper = TeamsScraper()
        scraper.session = db_session
        
        test_cases = [
            ("/en/squads/18bb7c10/Arsenal-Stats", "18bb7c10"),
            ("/en/squads/19538871/Manchester-United-Stats", "19538871"),
            ("/en/squads/206d90db/Chelsea-Stats", "206d90db")
        ]
        
        for url, expected_id in test_cases:
            result = scraper.extract_fbref_id(url)
            assert result == expected_id, f"Failed for URL: {url}"

    def test_scrape_success_single_link(self, mocker, db_session):
        """Test successful teams scraping with single link per team."""
        scraper = TeamsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        db_session.add(nation)
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch('core.get_selected_nations', return_value=['England'])
        mocker.patch('core.get_rate_limit', return_value=2)

        mock_df = pd.DataFrame({
            'Squad': ['Arsenal', 'Chelsea'],
            'Gender': ['M', 'M']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        
        def mock_find_elements(_, string):
            if string in ['Arsenal', 'Chelsea']:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/squads/{string.lower()}-stats/')
                return [mock_link]
            return []
        
        scraper.find_elements = mocker.Mock(side_effect=mock_find_elements)
        
        scraper.scrape()

        teams = db_session.query(Team).all()
        assert len(teams) == 2

        arsenal = db_session.query(Team).filter_by(name='Arsenal').first()
        assert arsenal is not None
        assert arsenal.gender == 'M'
        assert arsenal.nation_id == nation.id
        assert arsenal.fbref_url == '/en/squads/arsenal-stats/'

    def test_scrape_success_multiple_links(self, mocker, db_session):
        """Test teams scraping with multiple links per team name."""
        scraper = TeamsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        db_session.add(nation)
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch('core.get_selected_nations', return_value=['England'])
        mocker.patch('core.get_rate_limit', return_value=2)

        mock_df = pd.DataFrame({
            'Squad': ['Arsenal'],
            'Gender': ['F']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        
        def mock_find_elements(_, string):
            if string == 'Arsenal':
                mock_link_m = mocker.Mock()
                mock_link_m.__getitem__ = mocker.Mock(return_value='/en/squads/arsenal-m-stats/')
                
                mock_link_f = mocker.Mock()
                mock_link_f.__getitem__ = mocker.Mock(return_value='/en/squads/arsenal-f-stats/')
                
                mock_tr_f = mocker.Mock()
                mock_tr_f.find.return_value = mocker.Mock(get_text=mocker.Mock(return_value='F'))
                mock_link_f.parent.parent = mock_tr_f
                
                return [mock_link_m, mock_link_f]
            return []
        
        scraper.find_elements = mocker.Mock(side_effect=mock_find_elements)
        
        scraper.scrape()

        teams = db_session.query(Team).all()
        assert len(teams) == 1

        arsenal = db_session.query(Team).filter_by(name='Arsenal').first()
        assert arsenal is not None
        assert arsenal.gender == 'F'
        assert arsenal.fbref_url == '/en/squads/arsenal-f-stats/'

    def test_scrape_no_links_found(self, mocker, db_session):
        """Test handling when no links are found for a team."""
        scraper = TeamsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        db_session.add(nation)
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch('core.get_selected_nations', return_value=['England'])
        mocker.patch('core.get_rate_limit', return_value=2)

        mock_df = pd.DataFrame({
            'Squad': ['Unknown Team'],
            'Gender': ['M']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        
        scraper.find_elements = mocker.Mock(return_value=[])
        scraper.log_error = mocker.Mock()
        
        scraper.scrape()

        teams = db_session.query(Team).all()
        assert len(teams) == 0
        scraper.log_error.assert_called_once()

    def test_scrape_no_teams_found(self, mocker, db_session):
        """Test handling when no teams are found in HTML table."""
        scraper = TeamsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        db_session.add(nation)
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch('core.get_selected_nations', return_value=['England'])
        mocker.patch('core.get_rate_limit', return_value=2)

        mocker.patch('pandas.read_html', return_value=[])
        scraper.log_progress = mocker.Mock()
        
        scraper.scrape()

        teams = db_session.query(Team).all()
        assert len(teams) == 0
        scraper.log_progress.assert_called_with("No teams found for England")

    def test_scrape_multiple_nations(self, mocker, db_session):
        """Test processing multiple nations."""
        scraper = TeamsScraper()
        scraper.session = db_session
        
        england = NationFactory(name="England", country_code="ENG")
        france = NationFactory(name="France", country_code="FRA")
        db_session.add_all([england, france])
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch('core.get_selected_nations', return_value=['England', 'France'])
        mocker.patch('core.get_rate_limit', return_value=2)

        def mock_read_html(url):
            if "/en/countries/ENG/" in url:
                return [pd.DataFrame({'Squad': ['Arsenal'], 'Gender': ['M']})]
            else:
                return [pd.DataFrame({'Squad': ['PSG'], 'Gender': ['M']})]
        
        mocker.patch('pandas.read_html', side_effect=mock_read_html)
        
        def mock_find_elements(_, string):
            if string in ['Arsenal', 'PSG']:
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value=f'/en/squads/{string.lower()}-stats/')
                return [mock_link]
            return []
        
        scraper.find_elements = mocker.Mock(side_effect=mock_find_elements)
        
        scraper.scrape()

        teams = db_session.query(Team).all()
        assert len(teams) == 2

        arsenal = db_session.query(Team).filter_by(name='Arsenal').first()
        psg = db_session.query(Team).filter_by(name='PSG').first()
        
        assert arsenal is not None
        assert psg is not None
        assert arsenal.nation_id == england.id
        assert psg.nation_id == france.id

    def test_scrape_duplicate_handling(self, mocker, db_session):
        """Test that duplicate teams are handled correctly."""
        scraper = TeamsScraper()
        scraper.session = db_session
        nation = NationFactory(name="England", country_code="ENG")
        db_session.add(nation)
        db_session.commit()
        
        existing_team = Team(
            name="Arsenal",
            gender="M",
            fbref_id="existing_id",
            fbref_url="/en/squads/existing-arsenal/",
            nation_id=nation.id
        )
        db_session.add(existing_team)
        db_session.commit()

        mocker.patch('requests.get').return_value = mocker.Mock(
            text="<html><body><table></table></body></html>",
            status_code=200,
            raise_for_status=mocker.Mock()
        )
        mocker.patch('core.get_config').return_value = mocker.Mock(
            FBREF_BASE_URL="https://fbref.com"
        )
        mocker.patch('core.get_selected_nations', return_value=['England'])
        mocker.patch('core.get_rate_limit', return_value=2)

        mock_df = pd.DataFrame({
            'Squad': ['Arsenal'],
            'Gender': ['M']
        })
        mocker.patch('pandas.read_html', return_value=[mock_df])
        
        def mock_find_elements(_, string):
            if string == 'Arsenal':
                mock_link = mocker.Mock()
                mock_link.__getitem__ = mocker.Mock(return_value='/en/squads/arsenal-stats/')
                return [mock_link]
            return []
        
        scraper.find_elements = mocker.Mock(side_effect=mock_find_elements)
        
        scraper.scrape()

        teams_count = db_session.query(Team).count()
        assert teams_count == 1

        arsenal = db_session.query(Team).filter_by(name='Arsenal').first()
        assert arsenal.id == existing_team.id

    def test_log_progress_functionality(self, db_session):
        """Test logging progress functionality."""
        scraper = TeamsScraper()
        scraper.session = db_session
        
        scraper.log_progress("Processing teams...")
        scraper.log_progress("Team processing complete")

    def test_log_error_functionality(self, mocker, db_session):
        """Test logging error functionality."""
        scraper = TeamsScraper()
        scraper.session = db_session
        
        mocker.patch('core.base_scraper.is_debug_mode', return_value=False)
        
        test_exception = Exception("Test scraping error")
        scraper.log_error("scraping", test_exception)
