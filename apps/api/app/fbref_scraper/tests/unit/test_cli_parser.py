"""Unit tests for CLI parser utilities."""

from datetime import date

import pytest

from app.fbref_scraper.core.cli_parser import parse_arguments, parse_date, parse_nations


class TestParseArguments:
    """Test parse_arguments function."""

    def test_default_arguments(self, mocker):
        """Test parsing with no arguments (defaults)."""
        mocker.patch('sys.argv', ['script_name'])
        args = parse_arguments()
        
        assert args.mode == 'initial'
        assert args.days == 1
        assert args.from_date is None
        assert args.to_date is None
        assert args.nations is None
        assert args.from_year is None
        assert args.to_year is None
        assert args.resume is False
        assert args.continue_on_error is False

    def test_mode_argument(self, mocker):
        """Test parsing mode argument."""
        test_cases = [
            ('initial', 'initial'),
            ('daily', 'daily'),
            ('seasonal', 'seasonal')
        ]
        
        for mode_input, expected_mode in test_cases:
            mocker.patch('sys.argv', ['script_name', '--mode', mode_input])
            args = parse_arguments()
            assert args.mode == expected_mode

    def test_invalid_mode_argument(self, mocker):
        """Test parsing with invalid mode argument."""
        mocker.patch('sys.argv', ['script_name', '--mode', 'invalid'])
        with pytest.raises(SystemExit):
            parse_arguments()

    def test_days_argument(self, mocker):
        """Test parsing days argument."""
        mocker.patch('sys.argv', ['script_name', '--days', '7'])
        args = parse_arguments()
        assert args.days == 7

    def test_days_argument_invalid_type(self, mocker):
        """Test parsing days argument with invalid type."""
        mocker.patch('sys.argv', ['script_name', '--days', 'not_a_number'])
        with pytest.raises(SystemExit):
            parse_arguments()

    def test_date_arguments(self, mocker):
        """Test parsing date arguments."""
        mocker.patch('sys.argv', ['script_name', '--from-date', '2023-01-01', '--to-date', '2023-12-31'])
        args = parse_arguments()
        assert args.from_date == '2023-01-01'
        assert args.to_date == '2023-12-31'

    def test_nations_argument(self, mocker):
        """Test parsing nations argument."""
        mocker.patch('sys.argv', ['script_name', '--nations', 'England,France,Germany'])
        args = parse_arguments()
        assert args.nations == 'England,France,Germany'

    def test_year_arguments(self, mocker):
        """Test parsing year arguments."""
        mocker.patch('sys.argv', ['script_name', '--from-year', '2020', '--to-year', '2024'])
        args = parse_arguments()
        assert args.from_year == 2020
        assert args.to_year == 2024

    def test_year_arguments_invalid_type(self, mocker):
        """Test parsing year arguments with invalid type."""
        mocker.patch('sys.argv', ['script_name', '--from-year', 'not_a_year'])
        with pytest.raises(SystemExit):
            parse_arguments()

    def test_resume_flag(self, mocker):
        """Test parsing resume flag."""
        mocker.patch('sys.argv', ['script_name', '--resume'])
        args = parse_arguments()
        assert args.resume is True

    def test_continue_on_error_flag(self, mocker):
        """Test parsing continue-on-error flag."""
        mocker.patch('sys.argv', ['script_name', '--continue-on-error'])
        args = parse_arguments()
        assert args.continue_on_error is True

    def test_all_arguments_combined(self, mocker):
        """Test parsing all arguments together."""
        mocker.patch('sys.argv', [
            'script_name',
            '--mode', 'daily',
            '--days', '3',
            '--from-date', '2023-06-01',
            '--to-date', '2023-06-30',
            '--nations', 'England,Spain',
            '--from-year', '2022',
            '--to-year', '2023',
            '--resume',
            '--continue-on-error'
        ])
        args = parse_arguments()
        
        assert args.mode == 'daily'
        assert args.days == 3
        assert args.from_date == '2023-06-01'
        assert args.to_date == '2023-06-30'
        assert args.nations == 'England,Spain'
        assert args.from_year == 2022
        assert args.to_year == 2023
        assert args.resume is True
        assert args.continue_on_error is True


class TestParseDate:
    """Test parse_date function."""

    def test_valid_date_formats(self):
        """Test parsing valid date formats."""
        test_cases = [
            ('2023-01-01', date(2023, 1, 1)),
            ('2023-12-31', date(2023, 12, 31)),
            ('2024-02-29', date(2024, 2, 29)),
            ('2000-01-01', date(2000, 1, 1)),
            ('1999-12-31', date(1999, 12, 31))
        ]
        
        for date_str, expected_date in test_cases:
            result = parse_date(date_str)
            assert result == expected_date

    def test_invalid_date_formats(self):
        """Test parsing invalid date formats."""
        invalid_dates = [
            '2023/01/01',
            '01-01-2023',
            '2023-13-01',
            '2023-01-32',
            '2023-02-30',
            '2023-02-29',
            'not-a-date',
            '',
            '2023',
            '2023-01',
        ]
        
        for invalid_date in invalid_dates:
            with pytest.raises(ValueError, match="Invalid date format"):
                parse_date(invalid_date)

    def test_edge_case_dates(self):
        """Test edge case dates."""
        assert parse_date('2000-02-29') == date(2000, 2, 29)
        assert parse_date('1900-02-28') == date(1900, 2, 28)
        assert parse_date('1600-02-29') == date(1600, 2, 29)
        
        assert parse_date('2023-01-31') == date(2023, 1, 31)
        assert parse_date('2023-04-30') == date(2023, 4, 30)

    def test_error_message_format(self):
        """Test that error message includes the invalid date."""
        with pytest.raises(ValueError) as exc_info:
            parse_date('invalid-date')
        
        assert 'invalid-date' in str(exc_info.value)
        assert 'YYYY-MM-DD format' in str(exc_info.value)


class TestParseNations:
    """Test parse_nations function."""

    def test_single_nation(self):
        """Test parsing single nation."""
        result = parse_nations('England')
        assert result == ['England']

    def test_multiple_nations(self):
        """Test parsing multiple nations."""
        result = parse_nations('England,France,Germany')
        assert result == ['England', 'France', 'Germany']

    def test_nations_with_spaces(self):
        """Test parsing nations with spaces around commas."""
        result = parse_nations('England , France , Germany')
        assert result == ['England', 'France', 'Germany']

    def test_nations_with_extra_spaces(self):
        """Test parsing nations with extra spaces."""
        result = parse_nations('  England  ,  France  ,  Germany  ')
        assert result == ['England', 'France', 'Germany']

    def test_empty_string(self):
        """Test parsing empty string."""
        result = parse_nations('')
        assert result == ['']

    def test_single_comma(self):
        """Test parsing string with just a comma."""
        result = parse_nations(',')
        assert result == ['', '']

    def test_multiple_commas(self):
        """Test parsing string with multiple consecutive commas."""
        result = parse_nations('England,,France')
        assert result == ['England', '', 'France']

    def test_nations_with_special_characters(self):
        """Test parsing nations with special characters."""
        result = parse_nations('United States,South Korea,North Korea')
        assert result == ['United States', 'South Korea', 'North Korea']

    def test_nations_case_sensitivity(self):
        """Test that nation names preserve case."""
        result = parse_nations('england,FRANCE,germany')
        assert result == ['england', 'FRANCE', 'germany']

    def test_very_long_nation_list(self):
        """Test parsing a very long list of nations."""
        nations_str = ','.join([f'Nation{i}' for i in range(50)])
        result = parse_nations(nations_str)
        assert len(result) == 50
        assert result[0] == 'Nation0'
        assert result[49] == 'Nation49'


class TestCLIParserIntegration:
    """Integration tests for CLI parser functions."""

    def test_parse_arguments_with_date_validation(self, mocker):
        """Test that parse_arguments accepts date strings that parse_date can handle."""
        mocker.patch('sys.argv', ['script_name', '--from-date', '2023-01-01', '--to-date', '2023-12-31'])
        args = parse_arguments()
        
        assert args.from_date == '2023-01-01'
        assert args.to_date == '2023-12-31'
        
        from_date = parse_date(args.from_date)
        to_date = parse_date(args.to_date)
        
        assert from_date == date(2023, 1, 1)
        assert to_date == date(2023, 12, 31)

    def test_parse_arguments_with_nations_parsing(self, mocker):
        """Test that parse_arguments accepts nations string that parse_nations can handle."""
        mocker.patch('sys.argv', ['script_name', '--nations', 'England,France,Germany'])
        args = parse_arguments()
        
        assert args.nations == 'England,France,Germany'
        
        nations_list = parse_nations(args.nations)
        assert nations_list == ['England', 'France', 'Germany']

    def test_typical_workflow_scenarios(self, mocker):
        """Test typical CLI usage scenarios."""
        
        mocker.patch('sys.argv', ['script_name', '--mode', 'initial'])
        args = parse_arguments()
        assert args.mode == 'initial'
        assert args.resume is False
        
        mocker.patch('sys.argv', ['script_name', '--mode', 'daily', '--days', '7', '--resume'])
        args = parse_arguments()
        assert args.mode == 'daily'
        assert args.days == 7
        assert args.resume is True
        
        mocker.patch('sys.argv', ['script_name', '--mode', 'seasonal', '--nations', 'England,Spain'])
        args = parse_arguments()
        assert args.mode == 'seasonal'
        assert args.nations == 'England,Spain'
        
        mocker.patch('sys.argv', ['script_name', '--from-date', '2023-06-01', '--to-date', '2023-06-30', '--continue-on-error'])
        args = parse_arguments()
        assert args.from_date == '2023-06-01'
        assert args.to_date == '2023-06-30'
        assert args.continue_on_error is True

    def test_argument_help_text(self, mocker):
        """Test that help text is properly configured."""
        mocker.patch('sys.argv', ['script_name', '--help'])
        with pytest.raises(SystemExit) as exc_info:
            parse_arguments()
        
        assert exc_info.value.code == 0
