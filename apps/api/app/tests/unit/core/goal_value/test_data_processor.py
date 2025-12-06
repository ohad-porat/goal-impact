"""Unit tests for goal value data processor."""

from collections import defaultdict

from app.core.goal_value.data_processor import GoalDataProcessor
from app.tests.utils.factories import EventFactory, MatchFactory, PlayerFactory
from app.tests.utils.helpers import create_goal_event


class TestQueryGoals:
    """Tests for query_goals method."""

    def test_returns_goals_only(self, db_session):
        """Test that method returns only goal events."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory()
        player = PlayerFactory()
        goal = EventFactory(event_type="goal", match=match, player=player)
        db_session.commit()

        EventFactory(event_type="assist", match=match, player=player)
        EventFactory(event_type="yellow card", match=match, player=player)
        EventFactory(event_type="red card", match=match, player=player)
        db_session.commit()

        goals = processor.query_goals()

        assert len(goals) == 1
        assert goals[0].event_type == "goal"
        assert goals[0].id == goal.id

    def test_returns_own_goals(self, db_session):
        """Test that method returns own goal events."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory()
        player = PlayerFactory()
        own_goal = EventFactory(event_type="own goal", match=match, player=player)
        db_session.commit()

        goals = processor.query_goals()

        assert len(goals) == 1
        assert goals[0].event_type == "own goal"
        assert goals[0].id == own_goal.id

    def test_returns_both_goals_and_own_goals(self, db_session):
        """Test that method returns both goal and own goal events."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory()
        player = PlayerFactory()
        EventFactory(event_type="goal", match=match, player=player)
        EventFactory(event_type="own goal", match=match, player=player)
        db_session.commit()

        goals = processor.query_goals()

        assert len(goals) == 2
        goal_types = {g.event_type for g in goals}
        assert goal_types == {"goal", "own goal"}

    def test_returns_empty_list_when_no_goals(self, db_session):
        """Test that method returns empty list when no goals exist."""
        processor = GoalDataProcessor()
        processor.session = db_session

        goals = processor.query_goals()

        assert goals == []

    def test_excludes_other_event_types(self, db_session):
        """Test that method excludes non-goal event types."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory()
        player = PlayerFactory()
        EventFactory(event_type="assist", match=match, player=player)
        EventFactory(event_type="yellow card", match=match, player=player)
        EventFactory(event_type="red card", match=match, player=player)
        db_session.commit()

        goals = processor.query_goals()

        assert goals == []


class TestProcessGoalData:
    """Tests for process_goal_data method."""

    def test_aggregates_goals_by_minute_and_score_diff(self, db_session):
        """Test that goals are aggregated by (minute, score_diff) combination."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match1 = MatchFactory(home_team_goals=2, away_team_goals=1)
        match2 = MatchFactory(home_team_goals=2, away_team_goals=1)
        player = PlayerFactory()

        goal1 = create_goal_event(
            match1, player, minute=45, home_pre=0, home_post=1, away_pre=0, away_post=0
        )
        goal2 = create_goal_event(
            match2, player, minute=45, home_pre=0, home_post=1, away_pre=0, away_post=0
        )
        db_session.commit()

        goals = [goal1, goal2]
        aggregated_data = processor.process_goal_data(goals)

        key = (45, 1)
        assert key in aggregated_data
        assert aggregated_data[key]["total"] == 2
        assert aggregated_data[key]["win"] == 2
        assert aggregated_data[key]["draw"] == 0
        assert aggregated_data[key]["loss"] == 0

    def test_aggregates_different_outcomes(self, db_session):
        """Test that different outcomes (win/draw/loss) are counted separately."""
        processor = GoalDataProcessor()
        processor.session = db_session

        player = PlayerFactory()

        match1 = MatchFactory(home_team_goals=2, away_team_goals=1)
        goal1 = create_goal_event(
            match1, player, minute=45, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        match2 = MatchFactory(home_team_goals=1, away_team_goals=1)
        goal2 = create_goal_event(
            match2, player, minute=45, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        match3 = MatchFactory(home_team_goals=0, away_team_goals=2)
        goal3 = create_goal_event(
            match3, player, minute=45, home_pre=0, home_post=1, away_pre=0, away_post=0
        )

        db_session.commit()

        goals = [goal1, goal2, goal3]
        aggregated_data = processor.process_goal_data(goals)

        key = (45, 1)
        assert key in aggregated_data
        assert aggregated_data[key]["total"] == 3
        assert aggregated_data[key]["win"] == 1
        assert aggregated_data[key]["draw"] == 1
        assert aggregated_data[key]["loss"] == 1

    def test_handles_home_team_goals(self, db_session):
        """Test that home team goals are processed correctly."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory(home_team_goals=2, away_team_goals=0)
        player = PlayerFactory()
        goal = create_goal_event(
            match, player, minute=30, home_pre=0, home_post=1, away_pre=0, away_post=0
        )
        db_session.commit()

        goals = [goal]
        aggregated_data = processor.process_goal_data(goals)

        key = (30, 1)
        assert key in aggregated_data
        assert aggregated_data[key]["total"] == 1
        assert aggregated_data[key]["win"] == 1

    def test_handles_away_team_goals(self, db_session):
        """Test that away team goals are processed correctly."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory(home_team_goals=0, away_team_goals=2)
        player = PlayerFactory()
        goal = create_goal_event(
            match, player, minute=30, home_pre=0, home_post=0, away_pre=0, away_post=1
        )
        db_session.commit()

        goals = [goal]
        aggregated_data = processor.process_goal_data(goals)

        key = (30, 1)
        assert key in aggregated_data
        assert aggregated_data[key]["total"] == 1
        assert aggregated_data[key]["win"] == 1

    def test_filters_by_score_diff_range(self, db_session):
        """Test that goals outside score_diff range are excluded."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory(home_team_goals=10, away_team_goals=0)
        player = PlayerFactory()

        goal = create_goal_event(
            match, player, minute=30, home_pre=9, home_post=10, away_pre=0, away_post=0
        )
        db_session.commit()

        goals = [goal]
        aggregated_data = processor.process_goal_data(goals)

        key = (30, 10)
        assert key not in aggregated_data

    def test_includes_score_diff_at_boundaries(self, db_session):
        """Test that goals at score_diff boundaries are included."""
        processor = GoalDataProcessor()
        processor.session = db_session

        player = PlayerFactory()

        match1 = MatchFactory(home_team_goals=0, away_team_goals=3)
        goal1 = create_goal_event(
            match1, player, minute=30, home_pre=0, home_post=0, away_pre=2, away_post=3
        )

        match2 = MatchFactory(home_team_goals=5, away_team_goals=0)
        goal2 = create_goal_event(
            match2, player, minute=30, home_pre=4, home_post=5, away_pre=0, away_post=0
        )

        db_session.commit()

        goals = [goal1, goal2]
        aggregated_data = processor.process_goal_data(goals)

        assert (30, 3) in aggregated_data
        assert (30, 5) in aggregated_data

    def test_skips_invalid_goals(self, db_session):
        """Test that invalid goals are skipped."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory(home_team_goals=2, away_team_goals=1)
        player = PlayerFactory()

        valid_goal = create_goal_event(
            match, player, minute=30, home_pre=0, home_post=1, away_pre=0, away_post=0
        )
        db_session.commit()

        invalid_match = MatchFactory(home_team_goals=None, away_team_goals=1)
        invalid_goal = EventFactory(
            match=invalid_match,
            player=player,
            event_type="goal",
            minute=30,
            home_team_goals_pre_event=0,
            home_team_goals_post_event=1,
            away_team_goals_pre_event=0,
            away_team_goals_post_event=0,
        )
        db_session.commit()

        goals = [valid_goal, invalid_goal]
        aggregated_data = processor.process_goal_data(goals)

        key = (30, 1)
        assert key in aggregated_data
        assert aggregated_data[key]["total"] == 1

    def test_returns_empty_dict_when_no_goals(self, db_session):
        """Test that method returns empty defaultdict when no goals provided."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = processor.process_goal_data([])

        assert isinstance(aggregated_data, defaultdict)
        assert len(aggregated_data) == 0

    def test_handles_goals_at_different_minutes(self, db_session):
        """Test that goals at different minutes are aggregated separately."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory(home_team_goals=2, away_team_goals=1)
        player = PlayerFactory()

        goal1 = create_goal_event(
            match, player, minute=10, home_pre=0, home_post=1, away_pre=0, away_post=0
        )
        goal2 = create_goal_event(
            match, player, minute=90, home_pre=1, home_post=2, away_pre=0, away_post=0
        )
        db_session.commit()

        goals = [goal1, goal2]
        aggregated_data = processor.process_goal_data(goals)

        assert (10, 1) in aggregated_data
        assert (90, 2) in aggregated_data
        assert aggregated_data[(10, 1)]["total"] == 1
        assert aggregated_data[(90, 2)]["total"] == 1

    def test_handles_own_goals(self, db_session):
        """Test that own goals are processed correctly."""
        processor = GoalDataProcessor()
        processor.session = db_session

        match = MatchFactory(home_team_goals=0, away_team_goals=1)
        player = PlayerFactory()

        own_goal = EventFactory(
            match=match,
            player=player,
            event_type="own goal",
            minute=30,
            home_team_goals_pre_event=0,
            home_team_goals_post_event=0,
            away_team_goals_pre_event=0,
            away_team_goals_post_event=1,
        )
        db_session.commit()

        goals = [own_goal]
        aggregated_data = processor.process_goal_data(goals)

        key = (30, 1)
        assert key in aggregated_data
        assert aggregated_data[key]["total"] == 1


class TestGetSampleSizeForMinute:
    """Tests for get_sample_size_for_minute method."""

    def test_returns_total_for_minute(self, db_session):
        """Test that method returns total sample size for a minute."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (45, -1): {"total": 5},
            (45, 0): {"total": 10},
            (45, 1): {"total": 15},
            (46, 1): {"total": 20},
        }

        sample_size = processor.get_sample_size_for_minute(aggregated_data, 45)

        assert sample_size == 30

    def test_returns_zero_when_no_data(self, db_session):
        """Test that method returns 0 when minute has no data."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (45, 1): {"total": 10},
            (46, 1): {"total": 20},
        }

        sample_size = processor.get_sample_size_for_minute(aggregated_data, 50)

        assert sample_size == 0

    def test_returns_zero_for_empty_data(self, db_session):
        """Test that method returns 0 for empty aggregated_data."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {}

        sample_size = processor.get_sample_size_for_minute(aggregated_data, 45)

        assert sample_size == 0

    def test_sums_all_score_diffs(self, db_session):
        """Test that method sums across all score_diffs for the minute."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (45, -3): {"total": 1},
            (45, -2): {"total": 2},
            (45, -1): {"total": 3},
            (45, 0): {"total": 4},
            (45, 1): {"total": 5},
            (45, 2): {"total": 6},
            (45, 3): {"total": 7},
            (45, 4): {"total": 8},
            (45, 5): {"total": 9},
        }

        sample_size = processor.get_sample_size_for_minute(aggregated_data, 45)

        assert sample_size == 45


class TestGetWindowData:
    """Tests for get_window_data method."""

    def test_aggregates_single_minute(self, db_session):
        """Test that method aggregates data for a single minute window."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (45, 1): {"win": 5, "draw": 2, "loss": 3, "total": 10},
        }

        window_data = processor.get_window_data(aggregated_data, 45, 45)

        assert window_data[1]["win"] == 5
        assert window_data[1]["draw"] == 2
        assert window_data[1]["loss"] == 3
        assert window_data[1]["total"] == 10

    def test_aggregates_multiple_minutes(self, db_session):
        """Test that method aggregates data across multiple minutes."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (43, 1): {"win": 2, "draw": 1, "loss": 1, "total": 4},
            (44, 1): {"win": 3, "draw": 2, "loss": 1, "total": 5},
            (45, 1): {"win": 5, "draw": 2, "loss": 3, "total": 10},
            (46, 1): {"win": 1, "draw": 0, "loss": 1, "total": 2},
            (47, 1): {"win": 2, "draw": 1, "loss": 0, "total": 3},
        }

        window_data = processor.get_window_data(aggregated_data, 43, 47)

        assert window_data[1]["win"] == 13
        assert window_data[1]["draw"] == 6
        assert window_data[1]["loss"] == 6
        assert window_data[1]["total"] == 24

    def test_handles_partial_window(self, db_session):
        """Test that method handles windows with missing minutes."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (43, 1): {"win": 2, "draw": 1, "loss": 1, "total": 4},
            (45, 1): {"win": 5, "draw": 2, "loss": 3, "total": 10},
            (47, 1): {"win": 2, "draw": 1, "loss": 0, "total": 3},
        }

        window_data = processor.get_window_data(aggregated_data, 43, 47)

        assert window_data[1]["win"] == 9
        assert window_data[1]["draw"] == 4
        assert window_data[1]["loss"] == 4
        assert window_data[1]["total"] == 17

    def test_handles_empty_window(self, db_session):
        """Test that method returns zeros for empty window."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (50, 1): {"win": 10, "draw": 5, "loss": 5, "total": 20},
        }

        window_data = processor.get_window_data(aggregated_data, 43, 47)

        assert window_data[1]["win"] == 0
        assert window_data[1]["draw"] == 0
        assert window_data[1]["loss"] == 0
        assert window_data[1]["total"] == 0

    def test_aggregates_all_score_diffs(self, db_session):
        """Test that method aggregates data for all score_diffs."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (45, -1): {"win": 1, "draw": 1, "loss": 1, "total": 3},
            (45, 0): {"win": 2, "draw": 2, "loss": 2, "total": 6},
            (45, 1): {"win": 3, "draw": 3, "loss": 3, "total": 9},
        }

        window_data = processor.get_window_data(aggregated_data, 45, 45)

        assert window_data[-1]["total"] == 3
        assert window_data[0]["total"] == 6
        assert window_data[1]["total"] == 9

    def test_handles_boundary_minutes(self, db_session):
        """Test that method handles boundary minutes correctly."""
        processor = GoalDataProcessor()
        processor.session = db_session

        aggregated_data = {
            (1, 1): {"win": 1, "draw": 0, "loss": 0, "total": 1},
            (95, 1): {"win": 1, "draw": 0, "loss": 0, "total": 1},
        }

        window_data = processor.get_window_data(aggregated_data, 1, 1)
        assert window_data[1]["total"] == 1

        window_data = processor.get_window_data(aggregated_data, 95, 95)
        assert window_data[1]["total"] == 1
