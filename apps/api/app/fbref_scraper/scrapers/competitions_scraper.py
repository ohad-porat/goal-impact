"""Competitions scraper for FBRef data extraction."""

from typing import Optional, List
from app.models import Competition, Nation
from ..core import WebScraper, get_config, get_selected_nations, get_rate_limit, get_year_range


class CompetitionsScraper(WebScraper):
    def scrape(self, nations: Optional[List[str]] = None) -> None:
        """Scrape competition/league data."""
        nations = nations or get_selected_nations()
        
        config = get_config()
        url = f"{config.FBREF_BASE_URL}/en/countries/"
        self.load_page(url)
        
        country_th_elements = self.find_elements('th', {'scope': 'row', 'data-stat': 'country'})
        
        for row in country_th_elements:
            country_link = row.find('a')
            if not country_link:
                continue
                
            country_name = country_link.text
            
            if country_name not in nations:
                continue
            
            country = self.session.query(Nation).filter_by(name=country_name).first()
            if not country:
                self.log_progress(f"Nation {country_name} not found in database, skipping")
                continue
            
            country_url = f"{config.FBREF_BASE_URL}{country_link['href']}"
            self.log_progress(f"Processing competitions for {country_name}")
            
            df_list = self.fetch_html_table(country_url, get_rate_limit('heavy'))
            
            if not df_list:
                self.log_progress(f"No leagues found for: {country_name}")
                continue
            
            for league_tuple in df_list[0].iterrows():
                league = league_tuple[1]
                
                if league['Tier'] != '1st' or league['Gender'] != 'M':
                    continue
                
                competition_link = self.soup.find('a', string=f"{league['Competition Name']} ({league['Gender']})")
                if not competition_link:
                    continue
                    
                fbref_url = competition_link['href']
                self._persist_competition(country, league, "League", league['Tier'], fbref_url)
    
    def _persist_competition(self, nation: Nation, competition_data, comp_type: str, tier: str, fbref_url: str) -> None:
        """Persist competition data to the database."""
        competition_fbref_id = self.extract_fbref_id(fbref_url)
        
        competition_dict = {
            'name': competition_data['Competition Name'],
            'gender': competition_data['Gender'],
            'competition_type': comp_type,
            'fbref_id': competition_fbref_id,
            'fbref_url': fbref_url,
            'nation_id': nation.id,
            'tier': tier,
        }
        
        self.find_or_create_record(
            Competition,
            {'fbref_id': competition_fbref_id},
            competition_dict,
            f"competition: {competition_data['Competition Name']}"
        )
