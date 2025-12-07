"""Unit tests for StatsCalculationMetadata model."""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import StatsCalculationMetadata
from app.tests.utils.factories import StatsCalculationMetadataFactory


class TestStatsCalculationMetadataModel:
    """Test StatsCalculationMetadata model functionality."""

    def test_create_stats_metadata(self, db_session) -> None:
        """Test creating stats calculation metadata."""
        test_datetime = datetime(2024, 1, 15, 12, 0, 0)
        metadata = StatsCalculationMetadataFactory(
            calculation_date=test_datetime, total_goals_processed=5000, version="1.0.0"
        )
        db_session.commit()

        assert metadata.id is not None
        assert metadata.calculation_date == test_datetime
        assert metadata.total_goals_processed == 5000
        assert metadata.version == "1.0.0"

    def test_stats_metadata_required_fields(self, db_session) -> None:
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            metadata = StatsCalculationMetadata(version="1.0.0")
            db_session.add(metadata)
            db_session.commit()

    def test_stats_metadata_default_values(self, db_session) -> None:
        """Test creating metadata with factory defaults."""
        metadata = StatsCalculationMetadataFactory()
        db_session.commit()

        assert metadata.calculation_date is not None
        assert isinstance(metadata.calculation_date, datetime)
        assert metadata.total_goals_processed is not None
        assert metadata.total_goals_processed > 0
        assert metadata.version is not None

    def test_stats_metadata_multiple_entries(self, db_session) -> None:
        """Test that multiple metadata entries can be created."""
        metadata1 = StatsCalculationMetadataFactory(
            calculation_date=datetime(2024, 1, 15), version="1.0.0"
        )
        metadata2 = StatsCalculationMetadataFactory(
            calculation_date=datetime(2024, 1, 16), version="1.0.1"
        )
        db_session.commit()

        assert metadata1.id != metadata2.id
        assert metadata1.calculation_date != metadata2.calculation_date
        assert metadata1.version != metadata2.version
