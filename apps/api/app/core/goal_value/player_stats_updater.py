"""Player Stats Goal Value Updater - aggregates goal values for player stats."""

from app.core.database import Session
from app.models import Event, Match, PlayerStats


class PlayerStatsGoalValueUpdater:
    """Updates goal_value and gv_avg fields in player_stats table based on aggregated goal events."""
    
    def __init__(self):
        self.session = Session()
        self.aggregated_data = {}
        self.update_count = 0
        self.error_count = 0
        self.errors = []
        self.all_player_stats = None
    
    def run(self):
        """Main execution method to update player stats goal values."""
        print("Starting player stats goal value update process...")
        
        print("Aggregating goal values by player and season...")
        self._aggregate_player_goal_values()
        
        print("Updating player_stats records...")
        self._batch_update()
        
        self._print_summary()
        
        print("Player stats goal value update completed successfully!")
    
    def _aggregate_player_goal_values(self):
        """Calculate goal values for each player_stats record using optimized bulk query."""
        self.all_player_stats = self.session.query(PlayerStats).all()
        print(f"Found {len(self.all_player_stats)} player stats records to process")
        
        player_stats_lookup = {}
        for ps in self.all_player_stats:
            key = (ps.player_id, ps.season_id, ps.team_id)
            player_stats_lookup[key] = ps
        
        print("Created player stats lookup dictionary")
        
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
        
        for ps in self.all_player_stats:
            key = (ps.player_id, ps.season_id, ps.team_id)
            self.aggregated_data[key] = {
                'total_goal_value': 0.0,
                'gv_avg': 0.0,
                'goal_count': 0
            }
        
        print(f"Initialized {len(self.aggregated_data)} player-season-team combinations with zero values")
        
        processed_count = 0
        for event in goal_events_query:
            player_id, season_id, home_post, home_pre, away_post, away_pre, goal_value, home_team_id, away_team_id = event
            
            home_scored = home_post > home_pre
            away_scored = away_post > away_pre
            
            if home_scored and not away_scored:
                scoring_team_id = home_team_id
            elif away_scored and not home_scored:
                scoring_team_id = away_team_id
            else:
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
        """Batch update player_stats records with calculated goal values."""
        batch_size = 5000
        update_data = []
        
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
                try:
                    self.session.bulk_update_mappings(PlayerStats, update_data)
                    self.session.commit()
                    print(f"  Updated {len(update_data)} player stats records...")
                    update_data = []
                except Exception as e:
                    error_msg = f"Batch update error: {str(e)}"
                    self.errors.append(error_msg)
                    self.error_count += 1
                    update_data = []
        
        if update_data:
            try:
                self.session.bulk_update_mappings(PlayerStats, update_data)
                self.session.commit()
                print(f"  Updated final {len(update_data)} player stats records...")
            except Exception as e:
                error_msg = f"Final batch update error: {str(e)}"
                self.errors.append(error_msg)
                self.error_count += 1
    
    def _print_summary(self):
        """Print summary of the update process."""
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
