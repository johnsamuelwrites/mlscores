#
# SPDX-FileCopyrightText: 2026 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from mlscores.web.app import create_app


client = TestClient(create_app())


class TestEntitySearchRoute:
    """Tests for entity search suggestions endpoint."""

    @patch("mlscores.web.routes.urllib.request.urlopen")
    def test_search_entities_success(self, mock_urlopen):
        """Returns mapped search suggestions for valid query."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"""
        {
            "search": [
                {
                    "id": "Q1339",
                    "label": "Johann Sebastian Bach",
                    "description": "German composer",
                    "concepturi": "https://www.wikidata.org/wiki/Q1339"
                }
            ]
        }
        """
        mock_urlopen.return_value.__enter__.return_value = mock_response

        response = client.get(
            "/api/search/entities",
            params={"q": "Bach", "endpoint": "wikidata", "language": "en", "limit": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "Bach"
        assert data["endpoint"] == "wikidata"
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == "Q1339"

    def test_search_entities_rejects_unsupported_endpoint(self):
        """Rejects unsupported endpoint name."""
        response = client.get(
            "/api/search/entities",
            params={"q": "Bach", "endpoint": "custom"},
        )

        assert response.status_code == 400
        assert "supports only" in response.json()["detail"]

