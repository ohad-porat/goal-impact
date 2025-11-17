"""Players scraper for FBRef data extraction."""

import pandas as pd
from typing import Optional, List
from app.models import TeamStats, Player, PlayerStats, Season, Competition, Nation
from ..core import WebScraper, get_config, get_selected_nations, get_year_range


class PlayersScraper(WebScraper):
    def scrape(self, nations: Optional[List[str]] = None, from_year: Optional[int] = None, to_year: Optional[int] = None, update_mode: bool = False, seasonal_mode: bool = False, team_ids: Optional[set] = None) -> None:
        """Scrape player data and stats."""
        nations = nations or get_selected_nations()
        year_range = get_year_range()
        from_year = from_year or year_range[0]
        to_year = to_year or year_range[1]
        
        config = get_config()
        
        query = self.session.query(TeamStats).join(Season, TeamStats.season_id == Season.id) \
            .join(Competition, Season.competition_id == Competition.id) \
            .join(Nation, Competition.nation_id == Nation.id) \
            .filter(Nation.name.in_(nations)) \
            .filter(Season.start_year >= from_year, Season.start_year <= to_year) \
            .order_by(TeamStats.id.asc())
        
        if team_ids is not None:
            query = query.filter(TeamStats.team_id.in_(list(team_ids)))

        all_teams_stats = query.all()
        
        progress = self.load_progress()
        start_index = 0
        if progress and 'last_processed_index' in progress:
            start_index = progress['last_processed_index'] + 1
            self.log_progress(f"Resuming from index {start_index}")

        for index, team_stats in enumerate(all_teams_stats):
            if index < start_index:
                continue
                
            try:
                team_stats = self.session.merge(team_stats)
                self.log_progress(f"Processing players for {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")

                url = f"{config.FBREF_BASE_URL}{team_stats.fbref_url}"
                self.load_page(url)
                
                goal_logs_url = self._get_domestic_league_goal_logs_url(team_stats)
                team_stats.goal_logs_url = goal_logs_url
                self.session.commit()

                df_list = self.fetch_html_table(url)
                
                if not df_list:
                    self.log_progress(f"No player data found for {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
                    continue

                for players_tuple in df_list[0].iterrows():
                    player_series = players_tuple[1].to_frame().transpose()
                    player_name = player_series[('Unnamed: 0_level_0', 'Player')].iloc[0]
                    
                    if player_name == 'Squad Total' or player_name == 'Opponent Total':
                        continue

                    nation_string = player_series[('Unnamed: 1_level_0', 'Nation')].iloc[0]
                    player_country_code = None if pd.isnull(nation_string) else (nation_string.split(' ')[1] if ' ' in nation_string else nation_string)

                    if ('Playing Time', 'MP') in player_series.columns:
                        matches_played = player_series[('Playing Time', 'MP')].iloc[0]
                    elif ('Unnamed: 4_level_0', 'MP') in player_series.columns:
                        matches_played = player_series[('Unnamed: 4_level_0', 'MP')].iloc[0]
                    else:
                        continue
                    
                    matches_played = self._clean_integer_value(matches_played)
                    if matches_played is None or matches_played == 0:
                        self.log_skip("player", f"{player_name} {team_stats.season.start_year}-{team_stats.season.end_year}", "No matches played")
                        continue

                    player_a_tag = self.find_element('a', string=player_name)
                    if player_a_tag is None:
                        self.log_skip("player", f"{player_name} {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}", "No <a> tag found")
                        continue
                        
                    fbref_url = player_a_tag['href']
                    player_fbref_id = self.extract_fbref_id(fbref_url)

                    player_nation = self.session.query(Nation).filter_by(country_code=player_country_code).first()
                    nation_id = player_nation.id if player_nation is not None else None

                    player_dict = {
                        'name': player_name,
                        'fbref_id': player_fbref_id,
                        'fbref_url': fbref_url,
                        'nation_id': nation_id,
                    }

                    player = self.find_or_create_record(
                        Player,
                        {'fbref_id': player_fbref_id},
                        player_dict,
                        f"player: {player_name}"
                    )

                    player_stats_dict = {
                        'matches_played': matches_played,
                        'matches_started': self._clean_integer_value(self._get_player_stat_value(player_series, ('Playing Time', 'Starts'))),
                        'total_minutes': self._clean_integer_value(self._get_player_stat_value(player_series, ('Playing Time', 'Min'))),
                        'minutes_divided_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Playing Time', '90s'))),
                        'goals_scored': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'Gls'))),
                        'assists': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'Ast'))),
                        'total_goal_assists': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'G+A'))),
                        'non_pk_goals': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'G-PK'))),
                        'pk_made': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'PK'))),
                        'pk_attempted': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'PKatt'))),
                        'yellow_cards': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'CrdY'))),
                        'red_cards': self._clean_integer_value(self._get_player_stat_value(player_series, ('Performance', 'CrdR'))),
                        'xg': self._clean_float_value(self._get_player_stat_value(player_series, ('Expected', 'xG'))),
                        'non_pk_xg': self._clean_float_value(self._get_player_stat_value(player_series, ('Expected', 'npxG'))),
                        'xag': self._clean_float_value(self._get_player_stat_value(player_series, ('Expected', 'xAG'))),
                        'npxg_and_xag': self._clean_float_value(self._get_player_stat_value(player_series, ('Expected', 'npxG+xAG'))),
                        'progressive_carries': self._clean_integer_value(self._get_player_stat_value(player_series, ('Progression', 'PrgC'))),
                        'progressive_passes': self._clean_integer_value(self._get_player_stat_value(player_series, ('Progression', 'PrgP'))),
                        'progressive_passes_received': self._clean_integer_value(self._get_player_stat_value(player_series, ('Progression', 'PrgR'))),
                        'goal_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'Gls'))),
                        'assists_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'Ast'))),
                        'total_goals_assists_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'G+A'))),
                        'non_pk_goals_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'G-PK'))),
                        'non_pk_goal_and_assists_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'G+A-PK'))),
                        'xg_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'xG'))),
                        'xag_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'xAG'))),
                        'total_xg_xag_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'xG+xAG'))),
                        'non_pk_xg_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'npxG'))),
                        'npxg_and_xag_per_90': self._clean_float_value(self._get_player_stat_value(player_series, ('Per 90 Minutes', 'npxG+xAG'))),
                        'player_id': player.id,
                        'season_id': team_stats.season_id,
                        'team_id': team_stats.team_id,
                    }

                    if update_mode:
                        existing_player_stats = self.session.query(PlayerStats).filter_by(
                            player_id=player.id, 
                            season_id=team_stats.season_id, 
                            team_id=team_stats.team_id
                        ).first()
                        
                        if existing_player_stats:
                            stats_fields = [k for k in player_stats_dict.keys() if k not in ['player_id', 'season_id', 'team_id']]
                            for field in stats_fields:
                                if field in player_stats_dict:
                                    setattr(existing_player_stats, field, player_stats_dict[field])
                            try:
                                self.session.commit()
                                self.logger.info(f"Updated player stats: {player_name} {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
                            except Exception as e:
                                self.session.rollback()
                                self.logger.error(f"Error updating player stats: {e}")
                                raise
                        else:
                            self.find_or_create_record(
                                PlayerStats,
                                {'player_id': player.id, 'season_id': team_stats.season_id, 'team_id': team_stats.team_id},
                                player_stats_dict,
                                f"player stats: {player_name} {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}"
                            )
                            self.logger.info(f"Created new player stats: {player_name} {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
                    elif seasonal_mode:
                        self.find_or_create_record(
                            PlayerStats,
                            {'player_id': player.id, 'season_id': team_stats.season_id, 'team_id': team_stats.team_id},
                            player_stats_dict,
                            f"player stats: {player_name} {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}"
                        )
                        self.logger.info(f"Created new player stats: {player_name} {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
                    else:
                        self.find_or_create_record(
                            PlayerStats,
                            {'player_id': player.id, 'season_id': team_stats.season_id, 'team_id': team_stats.team_id},
                            player_stats_dict,
                            f"player stats: {player_name} {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}"
                        )
                
                self.save_progress({'last_processed_index': index})
                
            except Exception as e:
                self.log_error_and_continue("processing team", e, f"{team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
                continue
        
        self.clear_progress()
        self.log_progress("Players scraping completed successfully")

    def _get_domestic_league_goal_logs_url(self, team_stats) -> Optional[str]:
        """Get goal logs URL for domestic league only."""
        goal_logs_element = self.find_element('a', text='Goal Logs')
        if goal_logs_element:
            return goal_logs_element['href']
        
        li_elements = self.find_elements('li', class_='full hasmore')
        domestic_league_name = self.get_fbref_competition_name(team_stats.season.competition.name, team_stats.season.start_year)
        
        for li_element in li_elements:
            span_element = li_element.find('span', text='Goal Logs')
            if span_element:
                domestic_league_element = li_element.find('a', text=domestic_league_name)
                if domestic_league_element:
                    return domestic_league_element['href']
        
        self.log_progress(f"No domestic league goal logs found for {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
        return None

    def _get_player_stat_value(self, series, keys):
        """Extract player stat value from pandas series with error handling."""
        try:
            return series[keys].iloc[0]
        except (KeyError, IndexError):
            return None
