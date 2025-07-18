#!/usr/bin/env python3
"""
Comprehensive Unit Tests for utils module

This module contains thorough test cases for the utility functions:
- access_nested_map: Accesses nested dictionary structures safely
- get_json: Performs HTTP GET requests and returns JSON
- memoize: Caches method results for performance optimization

Each test case is documented with:
- Purpose of the test
- Input parameters being tested
- Expected behavior/output
- Special testing considerations
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    Test Suite for access_nested_map function

    This class verifies both successful dictionary access and proper
    error handling for invalid paths through nested dictionaries.
    """

    @parameterized.expand([
        # Test Case 1: Access top-level key
        (
            {"a": 1},         # nested_map: Simple 1-level dictionary
            ("a",),           # path: Tuple with single key
            1                # expected: Value at key 'a'
        ),
        # Test Case 2: Access nested dictionary
        (
            {"a": {"b": 2}}, # nested_map: 2-level nested dictionary
            ("a",),          # path: Access first level only
            {"b": 2}         # expected: Sub-dictionary at 'a'
        ),
        # Test Case 3: Access deeply nested value
        (
            {"a": {"b": 2}}, # nested_map: 2-level nested dictionary
            ("a", "b"),      # path: Full path to leaf node
            2                # expected: Value at deepest level
        )
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """
        Test successful access to nested dictionary structures

        Parameters:
            nested_map (dict): The dictionary to traverse
            path (tuple): Sequence of keys defining access path
            expected: The expected value at the end of path

        Behavior Verification:
            - Correct value is returned for valid paths
            - No exceptions raised for valid accesses
        """
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand([
        # Test Case 1: Missing top-level key
        (
            {},             # nested_map: Empty dictionary
            ("a",),         # path: Attempt to access missing key
            "Key 'a' not found"  # expected error message
        ),
        # Test Case 2: Missing nested key
        (
            {"a": 1},       # nested_map: Single-level dictionary
            ("a", "b"),     # path: Attempt invalid nested access
            "Key 'b' not found"  # expected error message
        )
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_msg):
        """
        Test proper KeyError raising for invalid dictionary paths

        Parameters:
            nested_map (dict): The dictionary to traverse
            path (tuple): Invalid access path
            expected_msg (str): Exact error message expected

        Behavior Verification:
            - KeyError is raised for invalid paths
            - Error message matches exactly with expected
            - Exception contains proper key name in message
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        
        # Verify both that an error was raised AND the message matches
        self.assertEqual(str(context.exception), expected_msg)


class TestGetJson(unittest.TestCase):
    """
    Test Suite for get_json function

    This class tests HTTP JSON fetching functionality with mock
    responses to avoid real network calls during testing.
    """

    @parameterized.expand([
        # Test Case 1: Basic JSON response
        (
            "http://example.com",   # test_url: Sample endpoint
            {"payload": True}       # test_payload: Simple response
        ),
        # Test Case 2: Different endpoint with false payload
        (
            "http://holberton.io",  # test_url: Alternative endpoint
            {"payload": False}      # test_payload: Different response
        )
    ])
    @patch('utils.requests.get')  # Mock the requests.get method
    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Test JSON retrieval from HTTP endpoints

        Parameters:
            test_url (str): URL being requested
            test_payload (dict): Expected JSON response
            mock_get (Mock): Injected mock of requests.get

        Behavior Verification:
            - requests.get is called exactly once with test_url
            - Returned JSON matches test_payload
            - External HTTP call is properly mocked
        """
        # Configure mock response object
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Execute the function under test
        result = get_json(test_url)

        # Verify mock was called correctly
        mock_get.assert_called_once_with(test_url)
        
        # Verify returned data matches expected payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Test Suite for memoize decorator

    Verifies that method results are properly cached to prevent
    redundant calculations or expensive operations.
    """

    def test_memoize(self):
        """
        Test that memoization caches method results

        Setup:
            - Test class with regular method and memoized property
            - Mock the underlying method to track calls

        Verification:
            - Underlying method is called only once
            - Subsequent calls return cached result
            - Return values remain correct
        """
        class TestClass:
            """Test class with memoized property"""

            def a_method(self):
                """Method to be memoized"""
                return 42

            @memoize
            def a_property(self):
                """Memoized property using a_method"""
                return self.a_method()

        # Patch a_method to track calls and control return value
        with patch.object(TestClass, 'a_method') as mock_method:
            # Configure mock and create test instance
            mock_method.return_value = 42
            test_instance = TestClass()

            # First access - should call a_method
            self.assertEqual(test_instance.a_property, 42)
            
            # Second access - should return cached result
            self.assertEqual(test_instance.a_property, 42)

            # Verify underlying method was called just once
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
