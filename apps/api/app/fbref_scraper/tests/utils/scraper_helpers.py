"""Helper utilities for testing scrapers."""

import pytest
from bs4 import BeautifulSoup


def create_mock_html_response(html_content: str, status_code: int = 200, mocker=None):
    """Create a mock HTTP response with HTML content."""
    if mocker is None:
        pytest.skip("mocker fixture required")
    mock_response = mocker.Mock()
    
    mock_response.text = html_content
    mock_response.status_code = status_code
    mock_response.raise_for_status = mocker.Mock()
    return mock_response


def create_mock_soup(html_content: str) -> BeautifulSoup:
    """Create a BeautifulSoup object from HTML content."""
    return BeautifulSoup(html_content, 'html.parser')


def mock_fbref_countries_page():
    """Return sample HTML for FBRef countries page."""
    return """
    <html>
    <body>
        <table id="countries">
            <thead>
                <tr>
                    <th>Country</th>
                    <th>Governing Body</th>
                    <th>Competitions</th>
                    <th>Clubs</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><a href="/en/countries/ENG/">England</a></td>
                    <td>FA</td>
                    <td data-stat="competitions">5</td>
                    <td data-stat="club_count"><a href="/en/countries/ENG/clubs/">92</a></td>
                </tr>
                <tr>
                    <td><a href="/en/countries/FRA/">France</a></td>
                    <td>FFF</td>
                    <td data-stat="competitions">4</td>
                    <td data-stat="club_count"><a href="/en/countries/FRA/clubs/">88</a></td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """


def mock_fbref_teams_page():
    """Return sample HTML for FBRef teams page."""
    return """
    <html>
    <body>
        <table id="teams">
            <thead>
                <tr>
                    <th>Squad</th>
                    <th>Gender</th>
                    <th>League</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><a href="/en/squads/18bb7c10/">Arsenal</a></td>
                    <td>M</td>
                    <td>Premier League</td>
                </tr>
                <tr>
                    <td><a href="/en/squads/19538871/">Chelsea</a></td>
                    <td>M</td>
                    <td>Premier League</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """


def mock_fbref_player_stats_page():
    """Return sample HTML for FBRef player stats page."""
    return """
    <html>
    <body>
        <table id="stats_standard">
            <thead>
                <tr>
                    <th>Player</th>
                    <th>Nation</th>
                    <th>MP</th>
                    <th>Starts</th>
                    <th>Min</th>
                    <th>Gls</th>
                    <th>Ast</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><a href="/en/players/12345678/">Bukayo Saka</a></td>
                    <td>ENG</td>
                    <td>38</td>
                    <td>35</td>
                    <td>3150</td>
                    <td>14</td>
                    <td>8</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def mock_requests_get(mocker):
    """Mock requests.get for testing HTTP calls."""
    return mocker.patch('requests.get')


@pytest.fixture
def mock_pandas_read_html(mocker):
    """Mock pandas.read_html for testing HTML table parsing."""
    return mocker.patch('pandas.read_html')
