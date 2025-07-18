#!/usr/bin/env python3
"""
Comprehensive Unit Tests for utils Module

This module implements thorough test cases for utility functions with:
- Complete parameterized test decorators
- Extensive docstrings explaining each test case
- Proper mocking of external dependencies
- pycodestyle compliant formatting
- Clear verification of all requirements
"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    Test Suite for access_nested_map Function

    Verifies both successful access patterns and proper error handling when
    navigating nested dictionary structures with key paths.
    """

    @parameterized.expand([
        # Test Case 1: Access top-level key in flat dictionary
        (
            {"a": 1},        # Input dictionary with single key
            ("a",),          # Path tuple accessing top level
            1                # Expected returned value
        ),
        # Test Case 2: Access nested dictionary structure
        (
            {"a": {"b": 2}}, # Input with two-level nesting
            ("a",),          # Path accessing first level
            {"b": 2}         # Expected nested dictionary
        ),
        # Test Case 3: Access leaf node in nested structure
        (
            {"a": {"b": 2}}, # Input with two-level nesting
            ("a", "b"),      # Full path to leaf node
            2                # Expected leaf value
        )
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """
        Verify Successful Dictionary Access Patterns

        Tests that access_nested_map correctly retrieves values when:
        - Accessing top-level keys
        - Navigating nested dictionaries
        - Retrieving leaf node values

        Asserts:
        - Returned value matches expected result
        - No exceptions raised for valid paths
        """
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

    @parameterized.expand([
        # Test Case 1: Missing top-level key
        (
            {},              # Empty dictionary
            ("a",),          # Attempt to access non-existent key
            "Key 'a' not found"  # Expected error message
        ),
        # Test Case 2: Missing nested key
        (
            {"a": 1},        # Flat dictionary
            ("a", "b"),      # Invalid nested access path
            "Key 'b' not found"  # Expected error message
        )
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_msg):
        """
        Verify Proper Error Handling for Invalid Paths

        Tests that access_nested_map:
        - Raises KeyError for invalid paths
        - Provides accurate error messages
        - Identifies missing keys correctly

        Asserts:
        - KeyError exception is raised
        - Exception message matches expected format
        - Correct key is identified in error message
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), expected_msg)


class TestGetJson(unittest.TestCase):
    """
    Test Suite for get_json Function

    Verifies HTTP JSON retrieval functionality while:
    - Preventing actual network calls through mocking
    - Validating request construction
    - Testing response handling
    """

    @parameterized.expand([
        # Test Case 1: Standard JSON response
        (
            "http://example.com",   # Test endpoint URL
            {"payload": True}       # Expected response payload
        ),
        # Test Case 2: Alternative endpoint
        (
            "http://holberton.io",  # Different test URL
            {"payload": False}     # Alternative response payload
        )
    ])
    @patch('utils.requests.get')  # Decorator to mock requests.get
    def test_get_json(self, test_url, test_payload, mock_get):
        """
        Verify JSON Retrieval from HTTP Endpoints

        Tests that get_json:
        - Makes correct HTTP GET requests
        - Properly processes JSON responses
        - Returns expected payloads

        Mock Configuration:
        - Creates mock response with json() method
        - Configures mock to return test payload
        - Verifies single call to requests.get

        Asserts:
        - Correct URL was requested
        - Return value matches test payload
        """
        # Configure mock response object
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Execute function under test
        result = get_json(test_url)

        # Verify mock interactions
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Test Suite for memoize Decorator

    Verifies correct implementation of method result caching:
    - Single execution of underlying method
    - Consistent return values
    - Proper cache behavior
    """

    def test_memoize(self):
        """
        Verify Method Result Caching Behavior

        Tests that @memoize decorator:
        - Only calls underlying method once
        - Returns cached result on subsequent calls
        - Maintains return value consistency

        Test Structure:
        1. Creates test class with memoized property
        2. Mocks underlying method
        3. Verifies call count and return values
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

        # Patch and test memoization behavior
        with patch.object(TestClass, 'a_method') as mock_method:
            mock_method.return_value = 42
            instance = TestClass()

            # First access - should call underlying method
            self.assertEqual(instance.a_property, 42)
            
            # Second access - should use cached result
            self.assertEqual(instance.a_property, 42)

            # Verify single call to underlying method
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
