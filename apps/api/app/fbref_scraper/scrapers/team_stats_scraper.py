"""Team stats scraper for FBRef data extraction."""

import math
from typing import Optional, List
from app.models import TeamStats, Season, Team, Nation, Competition
from ..core import WebScraper, get_config, get_selected_nations, get_year_range


class TeamStatsScraper(WebScraper):
    def scrape(self, nations: Optional[List[str]] = None, from_year: Optional[int] = None, to_year: Optional[int] = None, update_mode: bool = False, seasonal_mode: bool = False) -> None:
        """Scrape team stats data."""
        nations = nations or get_selected_nations()
        year_range = get_year_range()
        from_year = from_year or year_range[0]
        to_year = to_year or year_range[1]
        
        config = get_config()
        
        query = self.session.query(Season).join(Season.competition).join(Competition.nation)
        
        query = query.filter(Nation.name.in_(nations))
        
        query = query.filter(Season.start_year >= from_year, Season.start_year <= to_year)

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
                self.log_progress(f"Processing team stats for {season.competition.name} {season.start_year}-{season.end_year}")
                
                url = f"{config.FBREF_BASE_URL}{season.fbref_url}"
                self.load_page(url)
                
                matches_link = self.find_element('a', string='Scores & Fixtures')
                if matches_link and matches_link['href'] != '/en/matches/':
                    season.matches_url = matches_link['href']
                    self.session.commit()
                else:
                    season.matches_url = None
                    self.session.commit()

                if season.competition.competition_type == 'Cup':
                    continue

                df_list = self.fetch_html_table(url)
                
                if not df_list:
                    self.log_progress(f"No team stats found for {season.competition.name} {season.start_year}-{season.end_year}")
                    continue

                for team_stats_tuple in df_list[0].iterrows():
                    team_stats_data = team_stats_tuple[1]

                    if math.isnan(team_stats_data['Rk']):
                        continue

                    team_link = self.soup.select_one(f'td.left[data-stat="team"] a:-soup-contains("{team_stats_data["Squad"]}")')
                    if not team_link:
                        continue
                        
                    fbref_url = team_link['href']
                    team_fbref_id = self.extract_fbref_id(fbref_url)
                    
                    team_dict = {
                        'name': team_stats_data['Squad'],
                        'fbref_id': team_fbref_id,
                        'nation_id': season.competition.nation.id,
                    }

                    team = self.find_or_create_record(
                        Team,
                        {'fbref_id': team_fbref_id},
                        team_dict,
                        f"team: {team_stats_data['Squad']}"
                    )

                    team_stats_dict = {
                        'team_id': team.id,
                        'season_id': season.id,
                        'fbref_url': fbref_url,
                        'ranking': team_stats_data.get('Rk', None),
                        'matches_played': team_stats_data.get('MP', None),
                        'wins': team_stats_data.get('W', None),
                        'draws': team_stats_data.get('D', None),
                        'losses': team_stats_data.get('L', None),
                        'goals_for': team_stats_data.get('GF', None),
                        'goals_against': team_stats_data.get('GA', None),
                        'goal_difference': team_stats_data.get('GD', None),
                        'points': team_stats_data.get('Pts', None),
                        'points_per_match': team_stats_data.get('Pts/MP', None),
                        'xg': team_stats_data.get('xG', None),
                        'xga': team_stats_data.get('xGA', None),
                        'xgd': team_stats_data.get('xGD', None),
                        'xgd_per_90': team_stats_data.get('xGD/90', None)
                    }

                    if update_mode:
                        # Update existing team stats
                        existing_team_stats = self.session.query(TeamStats).filter_by(
                            team_id=team.id, 
                            season_id=season.id
                        ).first()
                        
                        if existing_team_stats:
                            # Update all stats fields
                            stats_fields = [k for k in team_stats_dict.keys() if k not in ['team_id', 'season_id']]
                            for field in stats_fields:
                                if field in team_stats_dict:
                                    setattr(existing_team_stats, field, team_stats_dict[field])
                            self.session.commit()
                            self.logger.info(f"Updated team stats: {team_stats_data['Squad']} {season.start_year}-{season.end_year}")
                        else:
                            self.logger.warning(f"No existing team stats found for {team_stats_data['Squad']} {season.start_year}-{season.end_year}")
                    elif seasonal_mode:
                        # Handle seasonal updates (URL changes and new seasons)
                        existing_team_stats = self.session.query(TeamStats).filter_by(
                            team_id=team.id, 
                            season_id=season.id
                        ).first()
                        
                        if existing_team_stats:
                            # Check if URL has changed
                            if existing_team_stats.fbref_url != fbref_url:
                                existing_team_stats.fbref_url = fbref_url
                                self.session.commit()
                                self.logger.info(f"Updated team stats URL: {team_stats_data['Squad']} {season.start_year}-{season.end_year}")
                        else:
                            # Create new team stats for new season
                            self.find_or_create_record(
                                TeamStats,
                                {'team_id': team.id, 'season_id': season.id},
                                team_stats_dict,
                                f"team stats: {team_stats_data['Squad']} {season.start_year}-{season.end_year}"
                            )
                            self.logger.info(f"Created new team stats: {team_stats_data['Squad']} {season.start_year}-{season.end_year}")
                    else:
                        # Normal initial mode
                        self.find_or_create_record(
                            TeamStats,
                            {'team_id': team.id, 'season_id': season.id},
                            team_stats_dict,
                            f"team stats: {team_stats_data['Squad']} {season.start_year}-{season.end_year}"
                        )
                
                self.save_progress({'last_processed_index': index})
                
            except Exception as e:
                self.log_error_and_continue("processing season", e, f"{season.competition.name} {season.start_year}-{season.end_year}")
                continue
        
        self.clear_progress()
        self.log_progress("Team stats scraping completed successfully")
