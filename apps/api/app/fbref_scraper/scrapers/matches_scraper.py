"""Matches scraper for FBRef data extraction."""

from datetime import datetime, date
from typing import Optional, List
from app.models import Match, Season, TeamStats, Nation, Competition
from ..core import WebScraper, get_config, get_selected_nations


class MatchesScraper(WebScraper):
    def scrape(self, nations: Optional[List[str]] = None, from_date: Optional[date] = None, to_date: Optional[date] = None) -> None:
        """Scrape match data."""
        nations = nations or get_selected_nations()
        
        config = get_config()
        
        query = self.session.query(Season).join(Competition).join(Nation)
        
        query = query.filter(Nation.name.in_(nations))
            
        all_seasons = query.all()
        
        progress = self.load_progress()
        start_index = 0
        if progress and 'last_processed_index' in progress:
            start_index = progress['last_processed_index'] + 1
            self.log_progress(f"Resuming from index {start_index}")

        for index, season in enumerate(all_seasons):
            if index < start_index:
                continue
                
            try:
                season = self.session.merge(season)
                self.log_progress(f"Processing matches for {season.competition.name} {season.start_year}-{season.end_year}")
                
                if not season.matches_url:
                    self.log_skip("season", f"{season.competition.name} {season.start_year}-{season.end_year}", "No matches URL available")
                    continue
                
                url = f"{config.FBREF_BASE_URL}{season.matches_url}"
                self.load_page(url)

                matches = self.soup.select('tr:not(.spacer)')
                matches_processed = 0
                
                for match in matches[1:]:
                    match_url_element = match.find('td', {'data-stat': 'score'})
                    if match_url_element is None:
                        continue
                        
                    match_fbref_url = match_url_element.a['href']
                    if 'play-off' in match_fbref_url.lower() or 'playoff' in match_fbref_url.lower():
                        continue
                        
                    match_fbref_id = self.extract_fbref_id(match_fbref_url)
                    
                    try:
                        home_team_goals, away_team_goals = match.find('td', {'data-stat': 'score'}).text.split('–')
                    except ValueError:
                        continue
                        
                    match_date = datetime.strptime(match.find('td', {'data-stat': 'date'}).text.strip(), '%Y-%m-%d').date()
                    
                    if from_date and match_date < from_date:
                        continue
                    if to_date and match_date > to_date:
                        continue
                        
                    home_team_url = match.find('td', {'data-stat': 'home_team'}).a['href']
                    home_team = self.session.query(TeamStats).filter_by(fbref_url=home_team_url).first()
                    away_team_url = match.find('td', {'data-stat': 'away_team'}).a['href']
                    away_team = self.session.query(TeamStats).filter_by(fbref_url=away_team_url).first()

                    if not home_team or not away_team:
                        continue

                    match_dict = {
                        'home_team_goals': home_team_goals,
                        'away_team_goals': away_team_goals,
                        'date': match_date,
                        'fbref_id': match_fbref_id,
                        'fbref_url': match_fbref_url,
                        'season_id': season.id,
                        'home_team_id': home_team.team.id,
                        'away_team_id': away_team.team.id
                    }

                    self.find_or_create_record(
                        Match,
                        {'fbref_id': match_fbref_id},
                        match_dict,
                        f"match: {home_team.team.name} vs {away_team.team.name} {match_date}"
                    )
                    matches_processed += 1
                    
                self.log_progress(f"Added {matches_processed} matches for {season.competition.name} {season.start_year}-{season.end_year}")
                
                self.save_progress({'last_processed_index': index})
                
            except Exception as e:
                self.log_error_and_continue("processing season", e, f"{season.competition.name} {season.start_year}-{season.end_year}")
                continue
        
        self.clear_progress()
        self.log_progress("Matches scraping completed successfully")
