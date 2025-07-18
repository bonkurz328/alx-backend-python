#!/usr/bin/env python3
"""
Comprehensive Test Suite for GithubOrgClient

This module contains complete unit and integration tests for the GithubOrgClient
class, verifying all specified functionality while maintaining:
- Proper test isolation with mocking
- Complete parameterized test cases
- Thorough documentation
- pycodestyle compliance
"""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock, Mock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit Test Suite for GithubOrgClient Class

    Tests individual methods with mocked dependencies to verify
    internal logic without making external HTTP calls.
    """

    @parameterized.expand([
        ("google", {"login": "google"}, "https://api.github.com/orgs/google"),
        ("abc", {"login": "abc"}, "https://api.github.com/orgs/abc"),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, expected_response, expected_url, mock_get_json):
        """
        Test that GithubOrgClient.org returns correct organization data

        Args:
            org_name: Name of the organization to test
            expected_response: The expected organization data
            expected_url: The URL that should be requested
            mock_get_json: Mock of the get_json function

        Verifies:
            - get_json is called exactly once with the correct URL
            - Returns the expected organization data
            - No actual HTTP calls are made
        """
        mock_get_json.return_value = expected_response

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_response)
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self):
        """
        Test that _public_repos_url property returns correct URL

        Verifies:
            - Returns the correct repos URL from organization payload
            - Uses the memoized org property
            - Properly handles the property access
        """
        test_payload = {"repos_url": "https://api.github.com/orgs/test/repos"}

        with patch('client.GithubOrgClient.org',
                  new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("test")
            self.assertEqual(
                client._public_repos_url,
                test_payload["repos_url"]
            )

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test that public_repos returns the correct list of repositories

        Args:
            mock_get_json: Mock of the get_json function

        Verifies:
            - Returns correct list of repository names
            - Uses _public_repos_url property
            - Calls get_json exactly once
            - Properly handles the repository data
        """
        test_repos = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
        ]
        mock_get_json.return_value = test_repos

        with patch('client.GithubOrgClient._public_repos_url',
                  new_callable=PropertyMock) as mock_url:
            mock_url.return_value = "https://api.github.com/orgs/test/repos"
            client = GithubOrgClient("test")
            self.assertEqual(client.public_repos(), ["repo1", "repo2"])
            mock_get_json.assert_called_once()
            mock_url.assert_called_once()

    @parameterized.expand([
        ({}, "my_license", False),
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test that has_license correctly identifies license presence

        Args:
            repo: Repository dictionary to test
            license_key: License key to check for
            expected: Expected boolean result

        Verifies:
            - Correctly handles missing license key
            - Properly matches license keys
            - Returns expected boolean result
        """
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration Test Suite for GithubOrgClient

    Tests complete functionality with mocked HTTP responses using
    fixtures from fixtures.py to simulate real API responses.
    """

    @classmethod
    def setUpClass(cls):
        """
        Class setup method - runs once before any tests

        Configures requests.get mock to return appropriate
        fixtures based on requested URLs
        """
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Determine which fixture to return based on URL"""
            if url.endswith("/orgs/google"):
                return Mock(json=lambda: cls.org_payload)
            if url.endswith("/orgs/google/repos"):
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: {})

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Class teardown method - runs after all tests complete

        Stops the patcher to restore original functionality
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """
        Test that public_repos returns expected repositories

        Verifies:
            - Returns complete list of expected repositories
            - Properly handles the integration between methods
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """
        Test public_repos with license filtering

        Verifies:
            - Correctly filters repositories by license
            - Returns only Apache 2.0 licensed repos
        """
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )


if __name__ == '__main__':
    unittest.main()
