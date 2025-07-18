#!/usr/bin/env python3
"""
Integration and Unit Tests for GithubOrgClient

This module contains complete test cases for GithubOrgClient class with:
- Unit tests for individual methods
- Integration tests with mocked external dependencies
- Parameterized test cases
- Proper fixture handling
"""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, PropertyMock, Mock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit Test Suite for GithubOrgClient Class

    Tests individual methods with mocked dependencies
    to verify internal logic without external calls.
    """

    @parameterized.expand([
        ("google",),  # Test with google org
        ("abc",)      # Test with abc org
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """
        Test GithubOrgClient.org returns correct organization data

        Verifies:
        - get_json is called exactly once with correct URL
        - Returns the expected organization data
        - No actual HTTP calls are made

        Args:
            org_name: Organization name to test
            mock_get_json: Mock of get_json function
        """
        # Setup mock return value
        test_payload = {"login": org_name}
        mock_get_json.return_value = test_payload

        # Create client and call method
        client = GithubOrgClient(org_name)
        result = client.org

        # Verify mock was called correctly
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """
        Test GithubOrgClient._public_repos_url property

        Verifies:
        - Returns correct repos URL from organization payload
        - Uses the memoized org property
        """
        # Setup test payload
        test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}

        # Patch org property to return our test payload
        with patch('client.GithubOrgClient.org',
                  new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload

            # Create client and get repos URL
            client = GithubOrgClient("google")
            result = client._public_repos_url

            # Verify results
            self.assertEqual(result, test_payload["repos_url"])
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """
        Test GithubOrgClient.public_repos method

        Verifies:
        - Returns correct list of repositories
        - Uses _public_repos_url property
        - Calls get_json once for repos list
        """
        # Setup test data
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}}
        ]
        mock_get_json.return_value = repos_payload

        # Mock the _public_repos_url property
        with patch('client.GithubOrgClient._public_repos_url',
                  new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = "https://example.com/repos"

            # Create client and get public repos
            client = GithubOrgClient("google")
            result = client.public_repos()

            # Verify results
            expected_repos = ["repo1", "repo2"]
            self.assertEqual(result, expected_repos)
            mock_get_json.assert_called_once()
            mock_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Test GithubOrgClient.has_license method

        Verifies correct license detection in repository data

        Args:
            repo: Repository dictionary to test
            license_key: License key to check for
            expected: Expected boolean result
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration Test Suite for GithubOrgClient

    Tests complete functionality with mocked HTTP responses
    using fixtures from fixtures.py
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up class-level mocks before any tests run

        Configures requests.get mock to return appropriate
        fixtures based on requested URLs
        """
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Determine which fixture to return based on URL"""
            if url.endswith("/orgs/google"):
                return Mock(json=lambda: cls.org_payload)
            elif url.endswith("/orgs/google/repos"):
                return Mock(json=lambda: cls.repos_payload)
            return Mock(json=lambda: {})

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """
        Clean up after all tests have run

        Stops the patcher to restore original functionality
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repositories"""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filtering"""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
