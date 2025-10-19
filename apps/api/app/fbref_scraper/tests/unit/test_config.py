"""Unit tests for configuration management."""

import pytest

from core.config import (
    ScraperConfig, get_config, update_config, get_selected_nations,
    get_year_range, get_rate_limit, is_debug_mode, get_log_level, get_log_format
)


class TestScraperConfig:
    """Test ScraperConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ScraperConfig()
        
        assert config.SELECTED_NATIONS == ['Belgium', 'England', 'France', 'Germany', 'Italy', 'Netherlands', 'Portugal', 'Spain', 'United States']
        assert config.YEAR_RANGE == (1992, 2024)
        assert config.DEBUG is True
        assert config.DATABASE_URL == 'sqlite:///db/database.db'
        assert config.REQUEST_TIMEOUT == 60
        assert config.FBREF_BASE_URL == 'https://fbref.com'
        assert config.LOG_LEVEL == 'INFO'
        assert config.LOG_FORMAT == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        assert config.RATE_LIMITS == {
            'default': 4,
            'heavy': 8,
            'light': 2
        }

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ScraperConfig(
            SELECTED_NATIONS=['England', 'France'],
            YEAR_RANGE=(2020, 2024),
            DEBUG=False,
            DATABASE_URL='sqlite:///test.db',
            REQUEST_TIMEOUT=30,
            FBREF_BASE_URL='https://test.fbref.com',
            LOG_LEVEL='DEBUG',
            LOG_FORMAT='%(levelname)s: %(message)s',
            RATE_LIMITS={'default': 1, 'heavy': 2}
        )
        
        assert config.SELECTED_NATIONS == ['England', 'France']
        assert config.YEAR_RANGE == (2020, 2024)
        assert config.DEBUG is False
        assert config.DATABASE_URL == 'sqlite:///test.db'
        assert config.REQUEST_TIMEOUT == 30
        assert config.FBREF_BASE_URL == 'https://test.fbref.com'
        assert config.LOG_LEVEL == 'DEBUG'
        assert config.LOG_FORMAT == '%(levelname)s: %(message)s'
        assert config.RATE_LIMITS == {'default': 1, 'heavy': 2}


class TestConfigFunctions:
    """Test configuration utility functions."""

    def test_get_config(self):
        """Test get_config function."""
        config = get_config()
        assert isinstance(config, ScraperConfig)
        assert config.FBREF_BASE_URL == 'https://fbref.com'

    def test_update_config_valid_key(self):
        """Test updating configuration with valid key."""
        original_debug = get_config().DEBUG
        
        update_config(DEBUG=False)
        
        assert get_config().DEBUG is False
        
        update_config(DEBUG=original_debug)

    def test_update_config_invalid_key(self):
        """Test updating configuration with invalid key."""
        with pytest.raises(ValueError, match="Unknown configuration key"):
            update_config(INVALID_KEY="test")

    def test_get_selected_nations(self):
        """Test get_selected_nations function."""
        nations = get_selected_nations()
        assert isinstance(nations, list)
        assert 'England' in nations
        assert 'France' in nations
        assert 'Belgium' in nations
        assert 'United States' in nations

    def test_get_year_range(self):
        """Test get_year_range function."""
        year_range = get_year_range()
        assert isinstance(year_range, tuple)
        assert len(year_range) == 2
        assert year_range[0] == 1992
        assert year_range[1] == 2024

    def test_get_rate_limit_default(self):
        """Test get_rate_limit with default operation."""
        rate_limit = get_rate_limit()
        assert rate_limit == 4

    def test_get_rate_limit_specific_operation(self):
        """Test get_rate_limit with specific operation."""
        assert get_rate_limit('heavy') == 8
        assert get_rate_limit('light') == 2
        assert get_rate_limit('default') == 4

    def test_get_rate_limit_unknown_operation(self):
        """Test get_rate_limit with unknown operation."""
        rate_limit = get_rate_limit('unknown')
        assert rate_limit == 4

    def test_is_debug_mode(self):
        """Test is_debug_mode function."""
        debug_mode = is_debug_mode()
        assert isinstance(debug_mode, bool)
        assert debug_mode is True

    def test_get_log_level(self):
        """Test get_log_level function."""
        log_level = get_log_level()
        assert log_level == 'INFO'

    def test_get_log_format(self):
        """Test get_log_format function."""
        log_format = get_log_format()
        assert '%(asctime)s' in log_format
        assert '%(name)s' in log_format
        assert '%(levelname)s' in log_format
        assert '%(message)s' in log_format
