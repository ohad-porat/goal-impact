"""Unit tests for progress management utilities."""

import pytest
import json
import os
import tempfile
from datetime import datetime
from core.progress_manager import (
    save_scraping_progress,
    load_scraping_progress,
    clear_scraping_progress,
    get_scrapers_to_run,
    SCRAPING_PROGRESS_FILE
)


class TestSaveScrapingProgress:
    """Test save_scraping_progress function."""

    def test_save_progress_new_file(self, tmp_path, mocker):
        """Test saving progress to a new file."""
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(tmp_path / 'progress.json'))
        save_scraping_progress('test_scraper', True)
        
        assert os.path.exists(str(tmp_path / 'progress.json'))
        
        with open(str(tmp_path / 'progress.json'), 'r') as f:
            progress = json.load(f)
        
        assert 'test_scraper' in progress
        assert progress['test_scraper']['completed'] is True
        assert 'timestamp' in progress['test_scraper']

    def test_save_progress_existing_file(self, tmp_path, mocker):
        """Test saving progress to an existing file."""
        progress_file = tmp_path / 'progress.json'
        
        initial_progress = {
            'existing_scraper': {
                'completed': False,
                'timestamp': '2023-01-01T00:00:00'
            }
        }
        
        with open(progress_file, 'w') as f:
            json.dump(initial_progress, f)
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        save_scraping_progress('new_scraper', True)
        
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        
        assert 'existing_scraper' in progress
        assert 'new_scraper' in progress
        assert progress['new_scraper']['completed'] is True
        assert progress['existing_scraper']['completed'] is False

    def test_save_progress_overwrite_existing(self, tmp_path, mocker):
        """Test overwriting existing scraper progress."""
        progress_file = tmp_path / 'progress.json'
        
        initial_progress = {
            'test_scraper': {
                'completed': False,
                'timestamp': '2023-01-01T00:00:00'
            }
        }
        
        with open(progress_file, 'w') as f:
            json.dump(initial_progress, f)
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        save_scraping_progress('test_scraper', True)
        
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        
        assert progress['test_scraper']['completed'] is True
        assert progress['test_scraper']['timestamp'] != '2023-01-01T00:00:00'

    def test_save_progress_file_write_error(self, mocker):
        """Test handling of file write errors."""
        mock_file = mocker.mock_open()
        mock_file.side_effect = IOError("Permission denied")
        mocker.patch('builtins.open', mock_file)
        
        mock_logger = mocker.patch('core.progress_manager.logger')
        save_scraping_progress('test_scraper', True)
        mock_logger.warning.assert_called_once()

    def test_save_progress_json_error(self, tmp_path, mocker):
        """Test handling of JSON serialization errors."""
        progress_file = tmp_path / 'progress.json'
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        mocker.patch('json.dump', side_effect=TypeError("Object not serializable"))
        mock_logger = mocker.patch('core.progress_manager.logger')
        save_scraping_progress('test_scraper', True)
        mock_logger.warning.assert_called_once()


class TestLoadScrapingProgress:
    """Test load_scraping_progress function."""

    def test_load_progress_file_exists(self, tmp_path, mocker):
        """Test loading progress from existing file."""
        progress_file = tmp_path / 'progress.json'
        
        expected_progress = {
            'scraper1': {'completed': True, 'timestamp': '2023-01-01T00:00:00'},
            'scraper2': {'completed': False, 'timestamp': '2023-01-02T00:00:00'}
        }
        
        with open(progress_file, 'w') as f:
            json.dump(expected_progress, f)
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        progress = load_scraping_progress()
        
        assert progress == expected_progress

    def test_load_progress_file_not_exists(self, mocker):
        """Test loading progress when file doesn't exist."""
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', '/nonexistent/path.json')
        progress = load_scraping_progress()
        assert progress == {}

    def test_load_progress_file_read_error(self, mocker):
        """Test handling of file read errors."""
        mocker.patch('os.path.exists', return_value=True)
        mock_file = mocker.mock_open()
        mock_file.side_effect = IOError("Permission denied")
        mocker.patch('builtins.open', mock_file)
        
        mock_logger = mocker.patch('core.progress_manager.logger')
        progress = load_scraping_progress()
        assert progress == {}
        mock_logger.warning.assert_called_once()

    def test_load_progress_json_error(self, tmp_path, mocker):
        """Test handling of JSON parsing errors."""
        progress_file = tmp_path / 'progress.json'
        
        with open(progress_file, 'w') as f:
            f.write('invalid json content')
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        mock_logger = mocker.patch('core.progress_manager.logger')
        progress = load_scraping_progress()
        assert progress == {}
        mock_logger.warning.assert_called_once()


class TestClearScrapingProgress:
    """Test clear_scraping_progress function."""

    def test_clear_progress_file_exists(self, tmp_path, mocker):
        """Test clearing progress when file exists."""
        progress_file = tmp_path / 'progress.json'
        
        with open(progress_file, 'w') as f:
            json.dump({'test': 'data'}, f)
        
        assert os.path.exists(str(progress_file))
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        clear_scraping_progress()
        
        assert not os.path.exists(str(progress_file))

    def test_clear_progress_file_not_exists(self, mocker):
        """Test clearing progress when file doesn't exist."""
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', '/nonexistent/path.json')
        clear_scraping_progress()

    def test_clear_progress_file_error(self, mocker):
        """Test handling of file deletion errors."""
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.remove', side_effect=OSError("Permission denied"))
        mock_logger = mocker.patch('core.progress_manager.logger')
        clear_scraping_progress()
        mock_logger.warning.assert_called_once()


class TestGetScrapersToRun:
    """Test get_scrapers_to_run function."""

    def test_get_scrapers_no_resume(self):
        """Test getting scrapers when not resuming."""
        scrapers = get_scrapers_to_run(resume=False)
        
        assert isinstance(scrapers, list)
        assert len(scrapers) == 8
        
        expected_names = [
            'nations', 'competitions', 'teams', 'seasons',
            'team_stats', 'players', 'matches', 'events'
        ]
        
        for i, (name, scraper_class) in enumerate(scrapers):
            assert name == expected_names[i]
            assert scraper_class is not None

    def test_get_scrapers_resume_no_progress(self, mocker):
        """Test getting scrapers when resuming but no progress file exists."""
        mocker.patch('core.progress_manager.load_scraping_progress', return_value={})
        mock_logger = mocker.patch('core.progress_manager.logger')
        scrapers = get_scrapers_to_run(resume=True)
        
        assert len(scrapers) == 8
        mock_logger.info.assert_called_once()

    def test_get_scrapers_resume_partial_progress(self, mocker):
        """Test getting scrapers when resuming with partial progress."""
        progress = {
            'nations': {'completed': True, 'timestamp': '2023-01-01T00:00:00'},
            'competitions': {'completed': True, 'timestamp': '2023-01-02T00:00:00'},
            'teams': {'completed': False, 'timestamp': '2023-01-03T00:00:00'}
        }
        
        mocker.patch('core.progress_manager.load_scraping_progress', return_value=progress)
        mock_logger = mocker.patch('core.progress_manager.logger')
        scrapers = get_scrapers_to_run(resume=True)
        
        assert len(scrapers) == 6
        assert scrapers[0][0] == 'teams'
        mock_logger.info.assert_called_once()

    def test_get_scrapers_resume_all_completed(self, mocker):
        """Test getting scrapers when all are completed."""
        progress = {
            'nations': {'completed': True, 'timestamp': '2023-01-01T00:00:00'},
            'competitions': {'completed': True, 'timestamp': '2023-01-02T00:00:00'},
            'teams': {'completed': True, 'timestamp': '2023-01-03T00:00:00'},
            'seasons': {'completed': True, 'timestamp': '2023-01-04T00:00:00'},
            'team_stats': {'completed': True, 'timestamp': '2023-01-05T00:00:00'},
            'players': {'completed': True, 'timestamp': '2023-01-06T00:00:00'},
            'matches': {'completed': True, 'timestamp': '2023-01-07T00:00:00'},
            'events': {'completed': True, 'timestamp': '2023-01-08T00:00:00'}
        }
        
        mocker.patch('core.progress_manager.load_scraping_progress', return_value=progress)
        mock_logger = mocker.patch('core.progress_manager.logger')
        scrapers = get_scrapers_to_run(resume=True)
        
        assert len(scrapers) == 8
        assert scrapers[0][0] == 'nations'
        mock_logger.info.assert_called_once()

    def test_get_scrapers_resume_missing_completed_field(self, mocker):
        """Test getting scrapers when progress entry missing completed field."""
        progress = {
            'nations': {'timestamp': '2023-01-01T00:00:00'},
            'competitions': {'completed': True, 'timestamp': '2023-01-02T00:00:00'}
        }
        
        mocker.patch('core.progress_manager.load_scraping_progress', return_value=progress)
        mock_logger = mocker.patch('core.progress_manager.logger')
        scrapers = get_scrapers_to_run(resume=True)
        
        assert len(scrapers) == 8
        assert scrapers[0][0] == 'nations'
        mock_logger.info.assert_called_once()

    def test_get_scrapers_resume_false_completed(self, mocker):
        """Test getting scrapers when progress entry has completed=False."""
        progress = {
            'nations': {'completed': False, 'timestamp': '2023-01-01T00:00:00'},
            'competitions': {'completed': True, 'timestamp': '2023-01-02T00:00:00'}
        }
        
        mocker.patch('core.progress_manager.load_scraping_progress', return_value=progress)
        mock_logger = mocker.patch('core.progress_manager.logger')
        scrapers = get_scrapers_to_run(resume=True)
        
        assert len(scrapers) == 8
        assert scrapers[0][0] == 'nations'
        mock_logger.info.assert_called_once()


class TestProgressManagerIntegration:
    """Integration tests for progress manager functions."""

    def test_full_progress_cycle(self, tmp_path, mocker):
        """Test complete progress save/load/clear cycle."""
        progress_file = tmp_path / 'progress.json'
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        save_scraping_progress('test_scraper', True)
        
        progress = load_scraping_progress()
        assert 'test_scraper' in progress
        assert progress['test_scraper']['completed'] is True
        
        clear_scraping_progress()
        assert not os.path.exists(str(progress_file))
        
        progress = load_scraping_progress()
        assert progress == {}

    def test_multiple_scrapers_progress(self, tmp_path, mocker):
        """Test managing progress for multiple scrapers."""
        progress_file = tmp_path / 'progress.json'
        
        mocker.patch('core.progress_manager.SCRAPING_PROGRESS_FILE', str(progress_file))
        save_scraping_progress('scraper1', True)
        save_scraping_progress('scraper2', False)
        save_scraping_progress('scraper3', True)
        
        progress = load_scraping_progress()
        assert len(progress) == 3
        assert progress['scraper1']['completed'] is True
        assert progress['scraper2']['completed'] is False
        assert progress['scraper3']['completed'] is True
        
        timestamps = [progress[key]['timestamp'] for key in progress]
        assert len(set(timestamps)) == 3
