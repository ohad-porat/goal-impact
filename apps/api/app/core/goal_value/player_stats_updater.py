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
        self.players_with_goals_count = 0
        self.players_with_goal_value_count = 0
        self.all_player_stats = None
    
    def run(self):
        """Main execution method to update player stats goal values."""
        print("Starting player stats goal value update process...")
        
        print("Aggregating goal values by player and season...")
        self._aggregate_player_goal_values()
        
        print("Counting players with goals_scored > 0...")
        self._count_players_with_goals()
        
        print("Updating player_stats records...")
        self._batch_update()
        
        self._print_summary()
        
        print("Player stats goal value update completed successfully!")
    
    def _aggregate_player_goal_values(self):
        """Calculate goal values for each player_stats record."""
        self.all_player_stats = self.session.query(PlayerStats).all()
        
        for player_stat in self.all_player_stats:
            goal_events = self.session.query(Event).join(
                Match, Event.match_id == Match.id
            ).filter(
                Event.player_id == player_stat.player_id,
                Match.season_id == player_stat.season_id,
                Event.event_type == 'goal',
                Event.goal_value.isnot(None)
            ).all()
            
            team_goal_values = []
            for event in goal_events:
                home_scored = event.home_team_goals_post_event > event.home_team_goals_pre_event
                away_scored = event.away_team_goals_post_event > event.away_team_goals_pre_event
                
                if home_scored and not away_scored:
                    if event.match.home_team_id == player_stat.team_id:
                        team_goal_values.append(event.goal_value)
                elif away_scored and not home_scored:
                    if event.match.away_team_id == player_stat.team_id:
                        team_goal_values.append(event.goal_value)
            
            if team_goal_values:
                total_goal_value = sum(team_goal_values)
                gv_avg = total_goal_value / len(team_goal_values)
            else:
                total_goal_value = 0.0
                gv_avg = 0.0
            
            key = (player_stat.player_id, player_stat.season_id, player_stat.team_id)
            self.aggregated_data[key] = {
                'total_goal_value': total_goal_value,
                'gv_avg': gv_avg
            }
        
        print(f"Processed {len(self.aggregated_data)} player-season-team combinations")
    
    def _count_players_with_goals(self):
        """Count players with goals_scored > 0."""
        self.players_with_goals_count = self.session.query(PlayerStats).filter(
            PlayerStats.goals_scored > 0
        ).count()
        print(f"Found {self.players_with_goals_count} player-season records with goals_scored > 0")
    
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
                
                if data['total_goal_value'] > 0:
                    self.players_with_goal_value_count += 1
                
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
        print(f"Players with goal events (goal_value data): {len(self.aggregated_data)}")
        print(f"Players with goals_scored > 0: {self.players_with_goals_count}")
        print(f"Players updated with goal_value > 0: {self.players_with_goal_value_count}")
        print(f"Difference (goals_scored vs goal_value): {self.players_with_goals_count - self.players_with_goal_value_count}")
        print(f"Successfully updated player stats records: {self.update_count}")
        print(f"Records with errors: {self.error_count}")
        print(f"Total player stats records processed: {self.update_count + self.error_count}")
        
        if self.errors and len(self.errors) <= 10:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  - {error}")
        elif self.errors:
            print(f"\nShowing first 10 errors (total: {len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"  - {error}")
        
        print("="*60)
