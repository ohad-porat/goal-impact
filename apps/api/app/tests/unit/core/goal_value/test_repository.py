"""Unit tests for goal value repository."""

from collections import defaultdict

from app.core.goal_value.repository import GoalValueRepository
from app.core.goal_value.utils import MAX_MINUTE, MAX_SCORE_DIFF, MIN_MINUTE, MIN_SCORE_DIFF
from app.models import GoalValueLookup, StatsCalculationMetadata
from app.tests.utils.factories import GoalValueLookupFactory


class TestPersistGoalValues:
    """Tests for persist_goal_values method."""

    def test_persists_goal_values_to_database(self, db_session):
        """Test that goal values are persisted to database."""
        repository = GoalValueRepository()
        repository.session = db_session

        goal_value_dict = {
            45: {1: 0.75, 0: 0.5, -1: 0.25},
            90: {1: 0.8, 0: 0.4},
        }

        repository.persist_goal_values(goal_value_dict)

        lookup_records = db_session.query(GoalValueLookup).all()

        assert len(lookup_records) == 5

        lookup_dict = {(r.minute, r.score_diff): r.goal_value for r in lookup_records}
        assert lookup_dict[(45, 1)] == 0.75
        assert lookup_dict[(45, 0)] == 0.5
        assert lookup_dict[(45, -1)] == 0.25
        assert lookup_dict[(90, 1)] == 0.8
        assert lookup_dict[(90, 0)] == 0.4

    def test_deletes_existing_records_before_persisting(self, db_session):
        """Test that existing records are deleted before persisting new ones."""
        repository = GoalValueRepository()
        repository.session = db_session

        GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.5)
        GoalValueLookupFactory(minute=45, score_diff=0, goal_value=0.3)
        db_session.commit()

        goal_value_dict = {
            90: {1: 0.8},
        }

        repository.persist_goal_values(goal_value_dict)

        lookup_records = db_session.query(GoalValueLookup).all()
        assert len(lookup_records) == 1
        assert lookup_records[0].minute == 90
        assert lookup_records[0].score_diff == 1
        assert lookup_records[0].goal_value == 0.8

    def test_handles_empty_dict(self, db_session):
        """Test that empty dict deletes all records without creating new ones."""
        repository = GoalValueRepository()
        repository.session = db_session

        GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.5)
        db_session.commit()

        repository.persist_goal_values({})

        lookup_records = db_session.query(GoalValueLookup).all()
        assert len(lookup_records) == 0

    def test_handles_large_dataset(self, db_session):
        """Test that method handles large datasets correctly."""
        repository = GoalValueRepository()
        repository.session = db_session

        goal_value_dict = {}
        for minute in range(MIN_MINUTE, MAX_MINUTE + 1):
            goal_value_dict[minute] = {}
            for score_diff in range(MIN_SCORE_DIFF, MAX_SCORE_DIFF + 1):
                goal_value_dict[minute][score_diff] = 0.5

        repository.persist_goal_values(goal_value_dict)

        lookup_records = db_session.query(GoalValueLookup).all()
        expected_count = (MAX_MINUTE - MIN_MINUTE + 1) * (MAX_SCORE_DIFF - MIN_SCORE_DIFF + 1)
        assert len(lookup_records) == expected_count

    def test_commits_transaction(self, db_session):
        """Test that transaction is committed after persisting."""
        repository = GoalValueRepository()
        repository.session = db_session

        goal_value_dict = {45: {1: 0.75}}

        repository.persist_goal_values(goal_value_dict)

        lookup_records = db_session.query(GoalValueLookup).all()
        assert len(lookup_records) == 1
        assert lookup_records[0].minute == 45
        assert lookup_records[0].score_diff == 1
        assert lookup_records[0].goal_value == 0.75


class TestSaveMetadata:
    """Tests for save_metadata method."""

    def test_saves_metadata_with_default_version(self, db_session):
        """Test that metadata is saved with default version."""
        repository = GoalValueRepository()
        repository.session = db_session

        repository.save_metadata(total_goals=1000)

        metadata_records = db_session.query(StatsCalculationMetadata).all()
        assert len(metadata_records) == 1
        assert metadata_records[0].total_goals_processed == 1000
        assert metadata_records[0].version == "1.0"

    def test_saves_metadata_with_custom_version(self, db_session):
        """Test that metadata is saved with custom version."""
        repository = GoalValueRepository()
        repository.session = db_session

        repository.save_metadata(total_goals=2000, version="2.0")

        metadata_records = db_session.query(StatsCalculationMetadata).all()
        assert len(metadata_records) == 1
        assert metadata_records[0].total_goals_processed == 2000
        assert metadata_records[0].version == "2.0"

    def test_creates_multiple_metadata_records(self, db_session):
        """Test that multiple metadata records can be created."""
        repository = GoalValueRepository()
        repository.session = db_session

        repository.save_metadata(total_goals=1000)
        repository.save_metadata(total_goals=2000)

        metadata_records = db_session.query(StatsCalculationMetadata).all()
        assert len(metadata_records) == 2
        assert {r.total_goals_processed for r in metadata_records} == {1000, 2000}

    def test_commits_transaction(self, db_session):
        """Test that transaction is committed after saving metadata."""
        repository = GoalValueRepository()
        repository.session = db_session

        repository.save_metadata(total_goals=1000)

        metadata_records = db_session.query(StatsCalculationMetadata).all()
        assert len(metadata_records) == 1
        assert metadata_records[0].total_goals_processed == 1000


class TestLoadGoalValues:
    """Tests for load_goal_values method."""

    def test_loads_goal_values_from_database(self, db_session):
        """Test that goal values are loaded from database."""
        repository = GoalValueRepository()
        repository.session = db_session

        GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.75)
        GoalValueLookupFactory(minute=45, score_diff=0, goal_value=0.5)
        GoalValueLookupFactory(minute=90, score_diff=1, goal_value=0.8)
        db_session.commit()

        goal_value_dict = repository.load_goal_values()

        assert isinstance(goal_value_dict, defaultdict)
        assert goal_value_dict[45][1] == 0.75
        assert goal_value_dict[45][0] == 0.5
        assert goal_value_dict[90][1] == 0.8

    def test_returns_empty_dict_when_no_records(self, db_session):
        """Test that method returns empty defaultdict when no records exist."""
        repository = GoalValueRepository()
        repository.session = db_session

        goal_value_dict = repository.load_goal_values()

        assert isinstance(goal_value_dict, defaultdict)
        assert len(goal_value_dict) == 0

    def test_handles_large_dataset(self, db_session):
        """Test that method handles large datasets correctly."""
        repository = GoalValueRepository()
        repository.session = db_session

        for minute in range(1, 96):
            for score_diff in range(-3, 6):
                GoalValueLookupFactory(minute=minute, score_diff=score_diff, goal_value=0.5)
        db_session.commit()

        goal_value_dict = repository.load_goal_values()

        assert len(goal_value_dict) == 95
        assert len(goal_value_dict[45]) == 9
        assert goal_value_dict[45][1] == 0.5

    def test_returns_correct_structure(self, db_session):
        """Test that returned structure matches expected format."""
        repository = GoalValueRepository()
        repository.session = db_session

        GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.75)
        GoalValueLookupFactory(minute=45, score_diff=0, goal_value=0.5)
        db_session.commit()

        goal_value_dict = repository.load_goal_values()

        assert isinstance(goal_value_dict, defaultdict)
        assert isinstance(goal_value_dict[45], dict)
        assert goal_value_dict[45][1] == 0.75
        assert goal_value_dict[45][0] == 0.5

    def test_handles_missing_minutes(self, db_session):
        """Test that method handles missing minutes correctly."""
        repository = GoalValueRepository()
        repository.session = db_session

        GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.75)
        db_session.commit()

        goal_value_dict = repository.load_goal_values()

        assert goal_value_dict[45][1] == 0.75
        assert 90 not in goal_value_dict

    def test_handles_missing_score_diffs(self, db_session):
        """Test that method handles missing score_diffs correctly."""
        repository = GoalValueRepository()
        repository.session = db_session

        GoalValueLookupFactory(minute=45, score_diff=1, goal_value=0.75)
        db_session.commit()

        goal_value_dict = repository.load_goal_values()

        assert goal_value_dict[45][1] == 0.75
        assert 0 not in goal_value_dict[45]
