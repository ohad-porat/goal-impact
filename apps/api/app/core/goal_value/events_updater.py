"""Event Goal Value Updater - updates goal_value field in events table."""

from app.core.database import Session
from app.models import Event

from .repository import GoalValueRepository


class EventGoalValueUpdater:
    """Updates goal_value for all goal events based on lookup table."""

    def __init__(self):
        self.session = Session()
        self.repository = GoalValueRepository()
        self.goal_value_lookup = {}
        self.missing_data_count = 0
        self.calculation_errors = []

    def run(self):
        """Main execution method to update all goal values."""
        print("Starting goal value update process...")

        print("Loading goal value lookup table...")
        self.goal_value_lookup = self.repository.load_goal_values()
        print(f"Loaded lookup data for {len(self.goal_value_lookup)} minutes")

        print("Querying goal events...")
        goals = self._query_goal_events()
        print(f"Found {len(goals)} goal events to process")

        if len(goals) == 0:
            print("No goals found to process")
            return

        print("Calculating goal values...")
        update_data = self._calculate_goal_values(goals)

        print(f"Updating {len(update_data)} events in database...")
        self._batch_update(update_data)

        self._print_summary(len(goals), len(update_data))

        print("Goal value update completed successfully!")

    def _query_goal_events(self):
        """Query all goal events from the database."""
        return self.session.query(Event).filter(Event.event_type.in_(["goal", "own goal"])).all()

    def _calculate_goal_values(self, goals):
        """Calculate goal_value for each goal event."""
        update_data = []
        processed = 0

        for goal in goals:
            processed += 1

            if processed % 5000 == 0:
                print(f"  Processed {processed}/{len(goals)} goals...")

            goal_value = self._calculate_single_goal_value(goal)

            if goal_value is not None:
                update_data.append({"id": goal.id, "goal_value": goal_value})

        return update_data

    def _calculate_single_goal_value(self, goal):
        """Calculate goal_value for a single goal event."""
        if (
            goal.home_team_goals_pre_event is None
            or goal.home_team_goals_post_event is None
            or goal.away_team_goals_pre_event is None
            or goal.away_team_goals_post_event is None
        ):
            self.missing_data_count += 1
            return None

        home_scored = goal.home_team_goals_post_event > goal.home_team_goals_pre_event
        away_scored = goal.away_team_goals_post_event > goal.away_team_goals_pre_event

        if not (home_scored or away_scored):
            error_msg = f"Goal ID {goal.id}: No team's score increased (pre: {goal.home_team_goals_pre_event}-{goal.away_team_goals_pre_event}, post: {goal.home_team_goals_post_event}-{goal.away_team_goals_post_event})"
            self.calculation_errors.append(error_msg)
            return None

        if home_scored:
            score_diff_before = goal.home_team_goals_pre_event - goal.away_team_goals_pre_event
            score_diff_after = goal.home_team_goals_post_event - goal.away_team_goals_post_event
        else:
            score_diff_before = goal.away_team_goals_pre_event - goal.home_team_goals_pre_event
            score_diff_after = goal.away_team_goals_post_event - goal.home_team_goals_post_event

        wp_before = self._lookup_win_probability(goal.minute, score_diff_before, goal.id)
        wp_after = self._lookup_win_probability(goal.minute, score_diff_after, goal.id)

        if wp_before is None or wp_after is None:
            error_msg = f"Goal ID {goal.id}: Failed to lookup win probabilities (minute={goal.minute}, before_diff={score_diff_before}, after_diff={score_diff_after})"
            self.calculation_errors.append(error_msg)
            return None

        goal_value = wp_after - wp_before
        return round(goal_value, 3)

    def _lookup_win_probability(self, minute, score_diff, goal_id):
        """Lookup win probability from lookup table."""
        lookup_minute = min(minute, 95)

        if (
            lookup_minute in self.goal_value_lookup
            and score_diff in self.goal_value_lookup[lookup_minute]
        ):
            return self.goal_value_lookup[lookup_minute][score_diff]

        if (lookup_minute - 1) in self.goal_value_lookup and score_diff in self.goal_value_lookup[
            lookup_minute - 1
        ]:
            return self.goal_value_lookup[lookup_minute - 1][score_diff]

        if (lookup_minute + 1) in self.goal_value_lookup and score_diff in self.goal_value_lookup[
            lookup_minute + 1
        ]:
            return self.goal_value_lookup[lookup_minute + 1][score_diff]

        if score_diff < 0:
            return 0.0

        if score_diff > 0:
            return 1.0

        return 0.5

    def _batch_update(self, update_data):
        """Batch update events table with calculated goal values."""
        batch_size = 1000
        commit_every = 10000

        for i in range(0, len(update_data), batch_size):
            batch = update_data[i : i + batch_size]
            self.session.bulk_update_mappings(Event, batch)

            if (i + batch_size) % commit_every == 0:
                self.session.commit()
                print(f"  Committed {i + batch_size} updates...")

        self.session.commit()
        print(f"  Committed all {len(update_data)} updates")

    def _print_summary(self, total_goals, updated_goals):
        """Print summary of the update process."""
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total goals processed: {total_goals}")
        print(f"Successfully updated: {updated_goals}")
        print(f"Failed to update: {total_goals - updated_goals}")
        print(f"Missing goal count data: {self.missing_data_count}")
        print(f"Calculation errors: {len(self.calculation_errors)}")

        if self.calculation_errors and len(self.calculation_errors) <= 10:
            print("\nCalculation errors:")
            for error in self.calculation_errors:
                print(f"  - {error}")
        elif self.calculation_errors:
            print(f"\nShowing first 10 calculation errors (total: {len(self.calculation_errors)}):")
            for error in self.calculation_errors[:10]:
                print(f"  - {error}")

        print("=" * 60)

    def update_goal_values_for_events(self, event_ids: list):
        """Update goal values for specific event IDs."""
        if not event_ids:
            return

        try:
            if not self.goal_value_lookup:
                self.goal_value_lookup = self.repository.load_goal_values()

            goals = (
                self.session.query(Event)
                .filter(Event.id.in_(event_ids), Event.event_type.in_(["goal", "own goal"]))
                .all()
            )

            if not goals:
                return

            update_data = self._calculate_goal_values(goals)

            if update_data:
                self._batch_update(update_data)
        except Exception as e:
            self.calculation_errors.append(f"Error updating goal values for events: {e}")
            raise
