"""Seasons scraper for FBRef data extraction."""

from typing import Optional, List
from app.models import Competition, Season, Nation
from ..core import WebScraper, get_config, get_year_range, get_selected_nations


class SeasonsScraper(WebScraper):
    def scrape(self, nations: Optional[List[str]] = None, from_year: Optional[int] = None, to_year: Optional[int] = None, seasonal_mode: bool = False):
        """Scrape season data."""
        nations = nations or get_selected_nations()
        year_range = get_year_range()
        from_year = from_year or year_range[0]
        to_year = to_year or year_range[1]
        
        config = get_config()
        
        query = self.session.query(Competition).join(Nation)
        query = query.filter(Nation.name.in_(nations))
        all_competitions = query.all()

        for competition in all_competitions:
            competition = self.session.merge(competition)
            self.log_progress(f"Processing seasons for {competition.name}")
            
            url = f"{config.FBREF_BASE_URL}{competition.fbref_url}"
            self.load_page(url)
            
            df_list = self.fetch_html_table(url)
            
            if not df_list:
                self.log_progress(f"No seasons found for {competition.name}")
                continue

            for season_tuple in df_list[0].iloc[::-1].iterrows():
                season_data = season_tuple[1]
                
                season_str = str(season_data['Season'])
                
                if '-' in season_str:
                    start_year, end_year = map(int, season_str.split('-'))
                else:
                    start_year = int(season_str[:4])
                    end_year = int(season_str[:4])

                if start_year < from_year or start_year > to_year:
                    self.log_progress(f"Not scraping season {season_str} in {competition.name}. Out of range.")
                    continue

                season_link = self.find_element('a', string=season_str)
                if not season_link:
                    continue
                    
                fbref_url = season_link['href']

                season_dict = {
                    'start_year': start_year,
                    'end_year': end_year,
                    'fbref_url': fbref_url,
                    'competition_id': competition.id,
                }

                if seasonal_mode:
                    # Check if season already exists
                    existing_season = self.session.query(Season).filter_by(
                        start_year=start_year, 
                        end_year=end_year, 
                        competition_id=competition.id
                    ).first()
                    
                    if existing_season:
                        # Check if URL has changed (season became archived)
                        if existing_season.fbref_url != fbref_url:
                            existing_season.fbref_url = fbref_url
                            self.session.commit()
                            self.logger.info(f"Updated season URL to archived format: {season_str} for {competition.name}")
                        else:
                            self.log_skip("season", f"{season_str} for {competition.name}")
                    else:
                        # New season detected
                        self.find_or_create_record(
                            Season,
                            {'start_year': start_year, 'end_year': end_year, 'competition_id': competition.id},
                            season_dict,
                            f"season: {season_str} for {competition.name}"
                        )
                        self.logger.info(f"Created new season: {season_str} for {competition.name}")
                else:
                    # Normal initial mode
                    self.find_or_create_record(
                        Season,
                        {'start_year': start_year, 'end_year': end_year, 'competition_id': competition.id},
                        season_dict,
                        f"season: {season_str} for {competition.name}"
                    )
