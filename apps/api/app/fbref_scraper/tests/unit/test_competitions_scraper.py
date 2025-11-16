"""Unit tests for CompetitionsScraper."""

import pandas as pd

from app.fbref_scraper.scrapers.competitions_scraper import CompetitionsScraper
from app.tests.utils.factories import NationFactory
from app.models import Competition


class TestCompetitionsScraper:
    """Test CompetitionsScraper functionality."""

    def test_scrape_success(self, db_session, mocker):
        """Test successful competition scraping."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        england_nation = NationFactory(name="England", country_code='ENG')
        france_nation = NationFactory(name="France", country_code='FRA')
        db_session.add_all([england_nation, france_nation])
        db_session.commit()
        
        fake_th1 = mocker.MagicMock()
        fake_link1 = mocker.MagicMock()
        fake_link1.text = "England"
        fake_link1.__getitem__ = mocker.Mock(return_value="/en/countries/ENG/")
        fake_th1.find.return_value = fake_link1
        
        fake_th2 = mocker.MagicMock()
        fake_link2 = mocker.MagicMock()
        fake_link2.text = "France"  
        fake_link2.__getitem__ = mocker.Mock(return_value="/en/countries/FRA/")
        fake_th2.find.return_value = fake_link2
        
        fake_competition_link = mocker.MagicMock()
        fake_competition_link.__getitem__ = mocker.Mock(return_value='/en/comps/9/Premier-League/')
        scraper.soup = mocker.MagicMock()
        scraper.soup.find.return_value = fake_competition_link
        
        scraper.find_elements = mocker.Mock(return_value=[fake_th1, fake_th2])
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        
        competition_data = pd.DataFrame({
            'Competition Name': ['Premier League'],
            'Gender': ['M'],
            'Tier': ['1st']
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[competition_data])
        
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_selected_nations', return_value=['England', 'France'])
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_rate_limit', return_value=2)
        
        scraper.scrape()
        
        england_competitions = db_session.query(Competition).filter_by(nation_id=england_nation.id).all()
        assert len(england_competitions) == 1
        assert england_competitions[0].name == 'Premier League'

    def test_scrape_country_not_found(self, db_session, mocker):
        """Test handling when nation is not found in database."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        france_nation = NationFactory(name="France", country_code='FRA')
        db_session.add(france_nation)
        db_session.commit()
        
        fake_th = mocker.MagicMock()
        fake_link = mocker.MagicMock()
        fake_link.text = "England"
        fake_link.__getitem__ = mocker.Mock(return_value="/en/countries/ENG/")
        fake_th.find.return_value = fake_link
        
        scraper.find_elements = mocker.Mock(return_value=[fake_th])
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_selected_nations', return_value=['England'])
        
        scraper.scrape()
        
        scraper.log_progress.assert_called_with("Nation England not found in database, skipping")

    def test_scrape_no_competition_link(self, db_session, mocker):
        """Test handling when competition link is not found."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        england_nation = NationFactory(name="England", country_code='ENG')
        db_session.add(england_nation)
        db_session.commit()
        
        fake_th = mocker.MagicMock()
        fake_link = mocker.MagicMock()
        fake_link.text = "England"
        fake_link.__getitem__ = mocker.Mock(return_value="/en/countries/ENG/")
        fake_th.find.return_value = fake_link
        
        scraper.find_elements = mocker.Mock(return_value=[fake_th])
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        
        scraper.soup = mocker.Mock()
        scraper.soup.find.return_value = None
        
        competition_data = pd.DataFrame({
            'Competition Name': ['Unknown League'],
            'Gender': ['M'],
            'Tier': ['1st']
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[competition_data])
        
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_selected_nations', return_value=['England'])
        
        scraper.scrape()
        
        competitions = db_session.query(Competition).filter_by(nation_id=england_nation.id).all()
        assert len(competitions) == 0

    def test_scrape_no_leagues_found(self, db_session, mocker):
        """Test handling when no leagues data is found."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        england_nation = NationFactory(name="England", country_code='ENG')
        db_session.add(england_nation)
        db_session.commit()
        
        fake_th = mocker.MagicMock()
        fake_link = mocker.MagicMock()
        fake_link.text = "England"
        fake_link.__getitem__ = mocker.Mock(return_value="/en/countries/ENG/")
        fake_th.find.return_value = fake_link
        
        scraper.find_elements = mocker.Mock(return_value=[fake_th])
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        
        scraper.fetch_html_table = mocker.Mock(return_value=[])
        
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_selected_nations', return_value=['England'])
        
        scraper.scrape()
        
        scraper.log_progress.assert_called_with("No leagues found for: England")
        
        competitions = db_session.query(Competition).filter_by(nation_id=england_nation.id).all()
        assert len(competitions) == 0

    def test_scrape_filters_non_first_tier(self, db_session, mocker):
        """Test that non-first-tier competitions are filtered out."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        england_nation = NationFactory(name="England", country_code='ENG')
        db_session.add(england_nation)
        db_session.commit()
        
        fake_th = mocker.MagicMock()
        fake_link = mocker.MagicMock()
        fake_link.text = "England"
        fake_link.__getitem__ = mocker.Mock(return_value="/en/countries/ENG/")
        fake_th.find.return_value = fake_link
        
        scraper.find_elements = mocker.Mock(return_value=[fake_th])
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        
        competition_data = pd.DataFrame({
            'Competition Name': ['Championship'],
            'Gender': ['M'],
            'Tier': ['2nd']
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[competition_data])
        
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_selected_nations', return_value=['England'])
        
        scraper.scrape()
        
        competitions = db_session.query(Competition).filter_by(nation_id=england_nation.id).all()
        assert len(competitions) == 0

    def test_scrape_filters_women_leagues(self, db_session, mocker):
        """Test that women's leagues are filtered out."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        england_nation = NationFactory(name="England", country_code='ENG')
        db_session.add(england_nation)
        db_session.commit()
        
        fake_th = mocker.MagicMock()
        fake_link = mocker.MagicMock()
        fake_link.text = "England"
        fake_link.__getitem__ = mocker.Mock(return_value="/en/countries/ENG/")
        fake_th.find.return_value = fake_link
        
        scraper.find_elements = mocker.Mock(return_value=[fake_th])
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        
        competition_data = pd.DataFrame({
            'Competition Name': ['WSL'],
            'Gender': ['F'],
            'Tier': ['1st']
        })
        
        scraper.fetch_html_table = mocker.Mock(return_value=[competition_data])
        
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_selected_nations', return_value=['England'])
        
        scraper.scrape()
        
        competitions = db_session.query(Competition).filter_by(nation_id=england_nation.id).all()
        assert len(competitions) == 0

    def test_persist_competition(self, db_session, mocker):
        """Test competition persistence functionality."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        nation = NationFactory(name="England", country_code='ENG')
        db_session.add(nation)
        db_session.commit()
        
        competition_data = pd.Series({
            'Competition Name': 'Premier League',
            'Gender': 'M'
        })
        
        scraper.extract_fbref_id = mocker.Mock(return_value='Premier-League')
        scraper.find_or_create_record = mocker.Mock()
        
        scraper._persist_competition(
            nation, 
            competition_data, 
            "League", 
            "1st", 
            "/en/comps/9/Premier-League/"
        )
        
        scraper.find_or_create_record.assert_called_once()
        
        call_args = scraper.find_or_create_record.call_args
        competition_dict = call_args[0][2]
        
        assert competition_dict['name'] == 'Premier League'
        assert competition_dict['gender'] == 'M'
        assert competition_dict['competition_type'] == 'League'
        assert competition_dict['fbref_id'] == 'Premier-League'
        assert competition_dict['fbref_url'] == '/en/comps/9/Premier-League/'
        assert competition_dict['nation_id'] == nation.id
        assert competition_dict['tier'] == '1st'

    def test_selected_nations_filtering(self, db_session, mocker):
        """Test that only selected nations are processed."""
        scraper = CompetitionsScraper()
        scraper.session = db_session
        
        england_nation = NationFactory(name="England", country_code='ENG')
        france_nation = NationFactory(name="France", country_code='FRA')
        germany_nation = NationFactory(name="Germany", country_code='GER')
        db_session.add_all([england_nation, france_nation, germany_nation])
        db_session.commit()
        
        fake_th_list = []
        for name, code in [("England", "ENG"), ("France", "FRA"), ("Germany", "GER")]:
            fake_th = mocker.MagicMock()
            fake_link = mocker.MagicMock()
            fake_link.text = name
            fake_link.__getitem__ = mocker.Mock(return_value=f"/en/countries/{code}/")
            fake_th.find.return_value = fake_link
            fake_th_list.append(fake_th)
        
        scraper.find_elements = mocker.Mock(return_value=fake_th_list)
        scraper.load_page = mocker.Mock()
        scraper.log_progress = mocker.Mock()
        scraper.fetch_html_table = mocker.Mock(return_value=[])
        
        mocker.patch('app.fbref_scraper.scrapers.competitions_scraper.get_selected_nations', return_value=['England'])
        
        scraper.scrape()
        
        england_call_found = False
        for call in scraper.log_progress.call_args_list:
            if call[0] and "Processing competitions for England" in call[0][0]:
                england_call_found = True
                break
        assert england_call_found