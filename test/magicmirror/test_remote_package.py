#!/usr/bin/env python3

import datetime
import json
import unittest
from unittest.mock import MagicMock, patch

import requests
from faker import Faker

from mmpm.magicmirror.package import MagicMirrorPackage, RemotePackage

fake = Faker()


class TestRemotePackage(unittest.TestCase):
    @patch("mmpm.magicmirror.package.requests.head")
    @patch("mmpm.magicmirror.package.requests.Response")
    @patch("mmpm.magicmirror.package.json.loads")
    def test_health(self, mock_json_loads, mock_response, mock_head):
        data = {"rate": {"reset": 1234567890, "remaining": 5}}

        mock_response.status_code = 200
        mock_response.text = json.dumps(data)
        mock_json_loads.return_value = data
        mock_head.side_effect = [
            MagicMock(status_code=200),
            MagicMock(status_code=200),
        ]  # GitLab  # Bitbucket

        health = RemotePackage.health()

        self.assertEqual(
            health["github"]["warning"],
            "5 GitHub API requests remaining. Request count will reset at 2009-02-13 23:31:30",
        )
        self.assertEqual(health["gitlab"]["error"], "")
        self.assertEqual(health["bitbucket"]["error"], "")

    @patch("mmpm.magicmirror.package.requests.Response")
    @patch("mmpm.magicmirror.package.safe_get_request")
    def test_serialize(self, mock_safe_get_request, mock_response):
        package = MagicMock()
        package.repository = "https://github.com/user/repo.git"
        remote_package = RemotePackage(package)

        stars = fake.pyint()
        open_issues = fake.pyint()
        forks_count = fake.pyint()

        # Mocking the response for GitHub API
        mock_response.text = json.dumps(
            {
                "stargazers_count": stars,
                "open_issues": open_issues,
                "created_at": "2020-01-01T00:00:00Z",
                "updated_at": "2020-12-31T23:59:59Z",
                "forks_count": forks_count,
            }
        )
        mock_safe_get_request.return_value = mock_response

        details = remote_package.serialize()

        self.assertEqual(
            details,
            {
                "stars": stars,
                "issues": open_issues,
                "created": "2020-01-01",
                "last_updated": "2020-12-31",
                "forks": forks_count,
            },
        )

    def test_format_bitbucket_api_details(self):
        remote_package = RemotePackage(MagicMirrorPackage())
        data = {
            "created_on": "2020-01-01T00:00:00Z",
            "updated_on": "2020-12-31T23:59:59Z",
        }
        url = "https://api.bitbucket.org/2.0/repositories/user/repo"

        # Assuming the `safe_get_request` function is used to fetch additional data
        with patch("mmpm.magicmirror.package.safe_get_request") as mock_request:
            mock_request.return_value.text = json.dumps({"pagelen": 5})
            details = remote_package.__format_bitbucket_api_details__(data, url)

        self.assertEqual(
            details,
            {
                "stars": 5,
                "issues": 5,
                "created": "2020-01-01",
                "last_updated": "2020-12-31",
                "forks": 5,
            },
        )
