"""Player Stats Goal Value Updater."""

import logging
from app.core.database import Session
from app.models import Event, Match, PlayerStats
from .utils import get_scoring_team_id

logger = logging.getLogger(__name__)


class PlayerStatsGoalValueUpdater:
    """Updates goal_value and gv_avg fields in player_stats table."""
    
    def __init__(self):
        self.session = Session()
        self.aggregated_data = {}
        self.update_count = 0
        self.error_count = 0
        self.errors = []
        self.all_player_stats = None
    
    def run(self):
        """Update player stats goal values."""
        print("Starting player stats goal value update process...")
        
        print("Aggregating goal values by player and season...")
        self._aggregate_player_goal_values()
        
        print("Updating player_stats records...")
        self._batch_update()
        
        self._print_summary()
        
        print("Player stats goal value update completed successfully!")
    
    def _aggregate_player_goal_values(self):
        """Calculate goal values for each player_stats record."""
        self.all_player_stats = self.session.query(PlayerStats).all()
        print(f"Found {len(self.all_player_stats)} player stats records to process")
        
        goal_events_query = self.session.query(
            Event.player_id,
            Match.season_id,
            Event.home_team_goals_post_event,
            Event.home_team_goals_pre_event,
            Event.away_team_goals_post_event,
            Event.away_team_goals_pre_event,
            Event.goal_value,
            Match.home_team_id,
            Match.away_team_id
        ).join(
            Match, Event.match_id == Match.id
        ).filter(
            Event.event_type == 'goal',
            Event.goal_value.isnot(None)
        ).all()
        
        print(f"Found {len(goal_events_query)} goal events with goal values")
        
        for player_stat in self.all_player_stats:
            key = (player_stat.player_id, player_stat.season_id, player_stat.team_id)
            self.aggregated_data[key] = {
                'total_goal_value': 0.0,
                'gv_avg': 0.0,
                'goal_count': 0
            }
        
        print(f"Initialized {len(self.aggregated_data)} player-season-team combinations with zero values")
        
        processed_count = 0
        for event in goal_events_query:
            player_id, season_id, home_post, home_pre, away_post, away_pre, goal_value, home_team_id, away_team_id = event
            
            scoring_team_id = get_scoring_team_id(
                home_post, home_pre, away_post, away_pre,
                home_team_id, away_team_id
            )
            
            if scoring_team_id is None:
                continue
            
            key = (player_id, season_id, scoring_team_id)
            if key in self.aggregated_data:
                self.aggregated_data[key]['total_goal_value'] += goal_value
                self.aggregated_data[key]['goal_count'] += 1
            
            processed_count += 1
            if processed_count % 50000 == 0:
                print(f"Processed {processed_count}/{len(goal_events_query)} goal events...")
        
        for key, data in self.aggregated_data.items():
            if data['goal_count'] > 0:
                data['gv_avg'] = data['total_goal_value'] / data['goal_count']
        
        print(f"Processed {len(self.aggregated_data)} player-season-team combinations")
    
    def _batch_update(self):
        """Batch update player_stats records."""
        batch_size = 5000
        update_data = []
        total_updated = 0
        
        for player_stat in self.all_player_stats:
            try:
                key = (player_stat.player_id, player_stat.season_id, player_stat.team_id)
                data = self.aggregated_data[key]
                
                update_data.append({
                    'id': player_stat.id,
                    'goal_value': round(data['total_goal_value'], 3),
                    'gv_avg': round(data['gv_avg'], 3)
                })
                
                self.update_count += 1
                
            except Exception as e:
                error_msg = f"Player ID {player_stat.player_id}, Season ID {player_stat.season_id}: {str(e)}"
                self.errors.append(error_msg)
                self.error_count += 1
            
            if len(update_data) >= batch_size:
                total_updated = self._commit_batch(update_data, total_updated, False)
                update_data = []
        
        if update_data:
            self._commit_batch(update_data, total_updated, True)
    
    def _commit_batch(self, update_data: list, total_updated: int, is_final: bool) -> int:
        """Commit a batch of updates."""
        try:
            self.session.bulk_update_mappings(PlayerStats, update_data)
            self.session.commit()
            total_updated += len(update_data)
            prefix = "final " if is_final else ""
            print(f"  Updated {prefix}{total_updated} player stats records...")
            return total_updated
        except Exception as e:
            error_msg = f"{'Final ' if is_final else ''}Batch update error: {str(e)}"
            self.errors.append(error_msg)
            self.error_count += 1
            return total_updated
    
    def _print_summary(self):
        """Print update summary."""
        print("\n" + "="*60)
        print("PLAYER STATS GOAL VALUE UPDATE SUMMARY")
        print("="*60)
        print(f"Total player stats records processed: {self.update_count}")
        print(f"Records with goal_value > 0: {sum(1 for data in self.aggregated_data.values() if data['total_goal_value'] > 0)}")
        print(f"Records with goal_value = 0: {sum(1 for data in self.aggregated_data.values() if data['total_goal_value'] == 0)}")
        print(f"Records with errors: {self.error_count}")
        
        if self.errors and len(self.errors) <= 10:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        elif self.errors:
            print(f"\nShowing first 10 errors (total: {len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")
        
        print("="*60)
    
    def update_player_stats_for_combinations(self, combinations: list):
        """Update player stats goal values for specific (player_id, season_id, team_id) combinations. Recalculates from all goals (excluding own goals)."""
        if not combinations:
            return
        
        logger.info(f"Updating player stats for {len(combinations)} player-season-team combinations...")
        
        update_data = []
        
        for player_id, season_id, team_id in combinations:
            try:
                goal_events_query = self.session.query(
                    Event.goal_value,
                    Event.home_team_goals_post_event,
                    Event.home_team_goals_pre_event,
                    Event.away_team_goals_post_event,
                    Event.away_team_goals_pre_event,
                    Match.home_team_id,
                    Match.away_team_id
                ).join(
                    Match, Event.match_id == Match.id
                ).filter(
                    Event.player_id == player_id,
                    Event.event_type == 'goal',
                    Event.goal_value.isnot(None),
                    Match.season_id == season_id
                ).all()
                
                goal_events = []
                for event in goal_events_query:
                    goal_value, home_post, home_pre, away_post, away_pre, home_team_id, away_team_id = event
                    
                    scoring_team_id = get_scoring_team_id(
                        home_post, home_pre, away_post, away_pre,
                        home_team_id, away_team_id
                    )
                    
                    if scoring_team_id == team_id:
                        goal_events.append(goal_value)
                
                total_goal_value = sum(goal_events)
                goal_count = len(goal_events)
                
                if goal_count > 0:
                    gv_avg = total_goal_value / goal_count
                else:
                    gv_avg = 0.0
                
                player_stat = self.session.query(PlayerStats).filter_by(
                    player_id=player_id,
                    season_id=season_id,
                    team_id=team_id
                ).first()
                
                if player_stat:
                    update_data.append({
                        'id': player_stat.id,
                        'goal_value': round(total_goal_value, 3),
                        'gv_avg': round(gv_avg, 3)
                    })
            except Exception as e:
                logger.error(f"Error processing player_id={player_id}, season_id={season_id}, team_id={team_id}: {e}")
                self.error_count += 1
                continue
        
        if update_data:
            try:
                batch_size = 5000
                for i in range(0, len(update_data), batch_size):
                    batch = update_data[i:i + batch_size]
                    self.session.bulk_update_mappings(PlayerStats, batch)
                    self.session.commit()
                    logger.info(f"  Updated {min(i + batch_size, len(update_data))}/{len(update_data)} player stats records...")
            except Exception as e:
                logger.error(f"Error updating player stats batch: {e}")
                self.session.rollback()
                raise
        
        logger.info(f"Updated {len(update_data)} player stats records")
