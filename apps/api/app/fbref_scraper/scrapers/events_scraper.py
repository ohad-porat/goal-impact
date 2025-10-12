"""Events scraper for FBRef data extraction."""

from datetime import date
from typing import Optional, List
from app.models import Event, Match, Player, Season, TeamStats, Nation, Competition
from ..core import WebScraper, get_config, get_selected_nations


class EventsScraper(WebScraper):
    def scrape(self, nations: Optional[List[str]] = None, from_date: Optional[date] = None, to_date: Optional[date] = None):
        """Scrape goals and assists for each match."""
        nations = nations or get_selected_nations()
        
        config = get_config()
        
        query = self.session.query(TeamStats).join(Season, TeamStats.season_id == Season.id) \
            .join(Competition, Season.competition_id == Competition.id) \
            .join(Nation, Competition.nation_id == Nation.id) \
            .filter(Nation.name.in_(nations))

        all_team_stats = query.all()
        
        progress = self.load_progress()
        start_index = 0
        if progress and 'last_processed_index' in progress:
            start_index = progress['last_processed_index'] + 1
            self.log_progress(f"Resuming from index {start_index}")

        for index, team_stats in enumerate(all_team_stats):
            if index < start_index:
                continue
                
            try:
                team_stats = self.session.merge(team_stats)
                self.log_progress(f"Processing events for {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")

                if team_stats.goal_logs_url is None:
                    self.log_progress(f"Skipping {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year} - no goal logs URL")
                    continue
                    
                url = f"{config.FBREF_BASE_URL}{team_stats.goal_logs_url}"
                self.load_page(url)

                events = self.soup.select('#goallogs_for tr:not(.spacer):not(:has(th:-soup-contains("Rk")))')
                events_processed = 0
                
                for event in events[1:]:
                    match, scorer_element, scoring_player = self._extract_match_and_player(event)
                    if match and scoring_player:
                        if from_date and match.date < from_date:
                            continue
                        if to_date and match.date > to_date:
                            continue
                            
                        self.log_progress(f'Scraping events from {match.date} {match.home_team.name} vs {match.away_team.name}')
                        self._scrape_goal(event, scorer_element, match, scoring_player.id)

                        assisting_player_element = event.find('td', {'data-stat': 'assist'})
                        if assisting_player_element.text.strip() != '':
                            assisting_player_fbref_id = self.extract_fbref_id(assisting_player_element.find('a')['href'])
                            assisting_player = self.session.query(Player).filter(Player.fbref_id == assisting_player_fbref_id).first()
                            if assisting_player:
                                self._scrape_assist(event, match, assisting_player.id)
                        events_processed += 1
                        
                self.log_progress(f"Added {events_processed} events for {team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
                
                self.save_progress({'last_processed_index': index})
                
            except Exception as e:
                self.log_error_and_continue("processing team", e, f"{team_stats.team.name} {team_stats.season.start_year}-{team_stats.season.end_year}")
                continue
        
        self.clear_progress()
        self.log_progress("Events scraping completed successfully")

    def _parse_event_data(self, event):
        """Extract common event data from HTML element."""
        venue = event.find('td', {'data-stat': 'venue'}).text.strip()
        minute_text = event.find('td', {'data-stat': 'minute'}).text.strip()
        if '+' in minute_text:
            base_minute, extra_minute = map(int, minute_text.split('+'))
            minute = base_minute + extra_minute
        else:
            minute = int(minute_text)

        score_before_event = event.find('td', {'data-stat': 'score_before_event'}).text.strip()
        if score_before_event == '':
            team_scored, other_team = None, None
        else:
            team_scored, other_team = map(int, score_before_event.split('-'))

        if team_scored is None or other_team is None:
            home_goals_pre_event = away_goals_pre_event = home_goals_post_event = away_goals_post_event = None
        else:
            if venue == 'Home':
                home_goals_pre_event = team_scored
                away_goals_pre_event = other_team
                home_goals_post_event = team_scored + 1
                away_goals_post_event = other_team
            else:
                home_goals_pre_event = other_team
                away_goals_pre_event = team_scored
                home_goals_post_event = other_team
                away_goals_post_event = team_scored + 1

        return {
            'minute': minute,
            'home_goals_pre_event': home_goals_pre_event,
            'away_goals_pre_event': away_goals_pre_event,
            'home_goals_post_event': home_goals_post_event,
            'away_goals_post_event': away_goals_post_event,
        }

    def _scrape_goal(self, event, scorer_element, match, scoring_player_id):
        """Scrape goal event data from HTML element."""
        event_data = self._parse_event_data(event)

        xg_element = event.find('td', {'data-stat': 'xg_shot'})
        psxg_element = event.find('td', {'data-stat': 'psxg_shot'})
        if xg_element and xg_element.text.strip():
            xg = float(xg_element.text.strip())
            psxg = float(psxg_element.text.strip()) if psxg_element else None
            xg_difference = psxg - xg if psxg is not None and xg is not None else None
        else:
            xg, psxg, xg_difference = None, None, None

        if '(OG)' in scorer_element.text.strip():
            event_type = 'own goal'
        else:
            event_type = 'goal'

        goal_dict = {
            'event_type': event_type,
            'minute': event_data['minute'],
            'home_team_goals_pre_event': event_data['home_goals_pre_event'],
            'away_team_goals_pre_event': event_data['away_goals_pre_event'],
            'home_team_goals_post_event': event_data['home_goals_post_event'],
            'away_team_goals_post_event': event_data['away_goals_post_event'],
            'xg': xg,
            'post_shot_xg': psxg,
            'xg_difference': xg_difference,
            'match_id': match.id,
            'player_id': scoring_player_id,
        }

        self.find_or_create_record(
            Event,
            {'match_id': match.id, 'player_id': scoring_player_id, 'minute': event_data['minute'], 'event_type': event_type},
            goal_dict,
            f"goal event: {match.date} {match.home_team.name} vs {match.away_team.name}"
        )

    def _scrape_assist(self, event, match, assisting_player_id):
        """Scrape assist event data from HTML element."""
        event_data = self._parse_event_data(event)

        assist_dict = {
            'event_type': 'assist',
            'minute': event_data['minute'],
            'home_team_goals_pre_event': event_data['home_goals_pre_event'],
            'away_team_goals_pre_event': event_data['away_goals_pre_event'],
            'home_team_goals_post_event': event_data['home_goals_post_event'],
            'away_team_goals_post_event': event_data['away_goals_post_event'],
            'xg': None,
            'post_shot_xg': None,
            'xg_difference': None,
            'match_id': match.id,
            'player_id': assisting_player_id,
        }

        self.find_or_create_record(
            Event,
            {'match_id': match.id, 'player_id': assisting_player_id, 'minute': event_data['minute'], 'event_type': 'assist'},
            assist_dict,
            f"assist event: {match.date} {match.home_team.name} vs {match.away_team.name}"
        )

    def _extract_match_and_player(self, event):
        """Extract match and player information from event HTML element."""
        match_fbref_id = self.extract_fbref_id(event.find('td', {'data-stat': 'date'}).find('a')['href'])
        match = self.session.query(Match).filter(Match.fbref_id == match_fbref_id).first()

        scorer_element = event.find('td', {'data-stat': 'scorer'})
        scoring_player_url = scorer_element.find('a')['href']
        scoring_player_fbref_id = self.extract_fbref_id(scoring_player_url)
        scoring_player = self.session.query(Player).filter(Player.fbref_id == scoring_player_fbref_id).first()
        
        if scoring_player is None:
            player_dict = {
                'name': scorer_element.text,
                'fbref_id': scoring_player_fbref_id,
                'fbref_url': scoring_player_url,
            }

            scoring_player = self.find_or_create_record(
                Player,
                {'fbref_id': scoring_player_fbref_id},
                player_dict,
                f"player: {scorer_element.text}"
            )

        return match, scorer_element, scoring_player
