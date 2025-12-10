import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to sys.path so we can import functions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions.tmdb_client import (
    search_media_by_title,
    fetch_tmdb_object_details,
    parse_media_details,
    get_media_info
)

class TestTMDBClient(unittest.TestCase):

    # --- TEST 1: Parsing Logic (Mandi's Refactor) ---
    def test_parse_media_details_movie(self):
        """Test extraction of title and year from a standard movie response."""
        mock_data = {
            "title": "Inception",
            "release_date": "2010-07-16"
        }
        title, year = parse_media_details(mock_data, "movie")
        self.assertEqual(title, "Inception")
        self.assertEqual(year, 2010)

    def test_parse_media_details_tv(self):
        """Test extraction of name and year from a standard TV response."""
        mock_data = {
            "name": "Breaking Bad",
            "first_air_date": "2008-01-20"
        }
        title, year = parse_media_details(mock_data, "tv")
        self.assertEqual(title, "Breaking Bad")
        self.assertEqual(year, 2008)

    def test_parse_media_details_missing_date(self):
        """Test behavior when date is missing or invalid."""
        mock_data = {"title": "Unknown Movie"}
        # Should return title and 0 for year
        self.assertEqual(parse_media_details(mock_data, "movie"), ("Unknown Movie", 0))

        mock_data_bad_date = {"title": "TBD Movie", "release_date": ""}
        self.assertEqual(parse_media_details(mock_data_bad_date, "movie"), ("TBD Movie", 0))

    # --- TEST 2: API Integration (Martin's Task) ---
    @patch('functions.tmdb_client.tmdb.Search')
    def test_search_media_by_title_found(self, MockSearch):
        """Test searching for a title that exists."""
        mock_search_instance = MockSearch.return_value
        mock_search_instance.tv.return_value = {
            'results': [{'id': 123, 'name': 'Test Show'}]
        }

        results = search_media_by_title("Test Show", "tv")

        self.assertEqual(len(results), 1)
        self.assertTrue(results) 

    @patch('functions.tmdb_client.tmdb.Search')
    def test_search_media_by_title_empty(self, MockSearch):
        """Test searching for a title with no results."""
        mock_search_instance = MockSearch.return_value
        mock_search_instance.movie.return_value = {'results': []}

        results = search_media_by_title("Nonexistent Movie", "movie")
        self.assertEqual(results, [])

    # --- TEST 3: Error Handling & Edge Cases (Eshar's Task) ---
    @patch('functions.tmdb_client.tmdb.Movies')
    def test_fetch_details_network_error(self, MockMovies):
        """
        Simulate a network error (Exception) when fetching details.
        Should handle gracefully and return empty dict.
        """
        mock_instance = MockMovies.return_value
        mock_instance.info.side_effect = Exception("Network Timeout")

        result = fetch_tmdb_object_details(550, "movie")
        self.assertEqual(result, {})

    def test_get_media_info_integration(self):
        """
        Test the full flow of get_media_info using the refactored pieces.
        We assume fetch and parse work, just checking the handoff.
        """
        with patch('functions.tmdb_client.fetch_tmdb_object_details') as mock_fetch:
            with patch('functions.tmdb_client.parse_media_details') as mock_parse:

                # Setup return values
                mock_fetch.return_value = {"some": "data"}
                mock_parse.return_value = ("The Matrix", 1999)

                # Execute
                result = get_media_info(123, "movie")

                # Assert
                mock_fetch.assert_called_once_with(123, "movie")
                mock_parse.assert_called_once_with({"some": "data"}, "movie")
                self.assertEqual(result, ("The Matrix", 1999))

if __name__ == '__main__':
    unittest.main()
