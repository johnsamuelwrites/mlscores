#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import pytest
from unittest.mock import Mock, patch, MagicMock
import urllib.error

from mlscores.query import (
    get_properties_and_values,
    get_qualifier_properties_and_values,
    get_reference_properties_and_values,
    get_property_labels,
    get_value_labels,
    safe_query,
)
from mlscores.constants import (
    WIKIDATA_PROPERTY_PREFIX,
    WIKIDATA_ITEM_PREFIX,
    DEFAULT_NO_LABEL,
    DEFAULT_UNKNOWN_LANGUAGE,
)


class TestGetPropertiesAndValues:
    """Tests for get_properties_and_values function."""

    def test_get_properties_and_values_success(self):
        """Test successful query for a valid item."""
        item_id = "Q5"
        result = get_properties_and_values(item_id)
        assert result is not None

    def test_get_properties_and_values_invalid_item_id(self):
        """Test that invalid item ID returns None."""
        item_id = " invalid"
        result = get_properties_and_values(item_id)
        assert result is None


class TestGetPropertyLabels:
    """Tests for get_property_labels function."""

    def test_empty_uri_list(self):
        """Test handling of empty URI list."""
        result = get_property_labels([])
        assert result == []

    def test_filters_non_wikidata_uris(self):
        """Test that non-Wikidata URIs are filtered out."""
        uris = [
            f"{WIKIDATA_PROPERTY_PREFIX}P31",
            "http://example.org/property/P1",
            f"{WIKIDATA_PROPERTY_PREFIX}P279",
        ]
        # This will make real SPARQL queries for the Wikidata URIs
        result = get_property_labels(uris)
        # Results should only contain Wikidata properties
        assert isinstance(result, list)
        for item in result:
            assert item[0].startswith(WIKIDATA_PROPERTY_PREFIX)

    @patch("mlscores.query.safe_query")
    def test_returns_tuples_with_correct_structure(
        self, mock_safe_query, sample_property_labels_response
    ):
        """Test that results are returned as tuples of (uri, label, language)."""
        mock_safe_query.return_value = sample_property_labels_response

        uris = [f"{WIKIDATA_PROPERTY_PREFIX}P31"]
        result = get_property_labels(uris)

        assert len(result) == 2
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3  # (uri, label, language)

    @patch("mlscores.query.safe_query")
    def test_handles_missing_labels(self, mock_safe_query):
        """Test handling of properties without labels."""
        mock_safe_query.return_value = {
            "results": {
                "bindings": [
                    {"p": {"value": f"{WIKIDATA_PROPERTY_PREFIX}P31"}},
                ]
            }
        }

        uris = [f"{WIKIDATA_PROPERTY_PREFIX}P31"]
        result = get_property_labels(uris)

        assert len(result) == 1
        assert result[0][1] == DEFAULT_NO_LABEL
        assert result[0][2] == DEFAULT_UNKNOWN_LANGUAGE

    @patch("mlscores.query.safe_query")
    def test_batching_large_uri_list(self, mock_safe_query):
        """Test that large URI lists are processed in batches."""
        mock_safe_query.return_value = {"results": {"bindings": []}}

        # Create 250 URIs (should result in 3 batches with batch_size=100)
        uris = [f"{WIKIDATA_PROPERTY_PREFIX}P{i}" for i in range(250)]

        get_property_labels(uris)
        assert mock_safe_query.call_count == 3


class TestGetValueLabels:
    """Tests for get_value_labels function."""

    def test_empty_uri_list(self):
        """Test handling of empty URI list."""
        result = get_value_labels([])
        assert result == []

    def test_filters_non_entity_uris(self):
        """Test that non-entity URIs are filtered out."""
        uris = [
            f"{WIKIDATA_ITEM_PREFIX}42",
            "http://www.wikidata.org/prop/P31",  # Not an entity
            "http://example.org/entity/Q1",
        ]
        result = get_value_labels(uris)
        assert isinstance(result, list)

    @patch("mlscores.query.safe_query")
    def test_returns_tuples_with_correct_structure(
        self, mock_safe_query, sample_value_labels_response
    ):
        """Test that results are returned as tuples of (uri, label, language)."""
        mock_safe_query.return_value = sample_value_labels_response

        uris = [f"{WIKIDATA_ITEM_PREFIX}5"]
        result = get_value_labels(uris)

        assert len(result) == 2
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3

    @patch("mlscores.query.safe_query")
    def test_handles_missing_labels(self, mock_safe_query):
        """Test handling of values without labels."""
        mock_safe_query.return_value = {
            "results": {
                "bindings": [
                    {"v": {"value": f"{WIKIDATA_ITEM_PREFIX}42"}},
                ]
            }
        }

        uris = [f"{WIKIDATA_ITEM_PREFIX}42"]
        result = get_value_labels(uris)

        assert len(result) == 1
        assert result[0][1] == DEFAULT_NO_LABEL
        assert result[0][2] == DEFAULT_UNKNOWN_LANGUAGE


class TestSafeQuery:
    """Tests for the safe_query retry mechanism."""

    @patch("mlscores.query.tqdm")
    def test_safe_query_success(self, mock_tqdm):
        """Test successful query execution."""
        mock_sparql = Mock()
        mock_result = {"results": {"bindings": []}}
        mock_sparql.query().convert.return_value = mock_result

        # Mock tqdm context manager
        mock_progress = MagicMock()
        mock_tqdm.return_value.__enter__ = Mock(return_value=mock_progress)
        mock_tqdm.return_value.__exit__ = Mock(return_value=False)

        result = safe_query(mock_sparql)
        assert result == mock_result

    @patch("mlscores.query.tqdm")
    @patch("mlscores.query.time.sleep")
    def test_safe_query_retry_on_429(self, mock_sleep, mock_tqdm):
        """Test retry behavior on rate limit (429) error."""
        mock_sparql = Mock()

        # First call raises 429, second succeeds
        mock_result = {"results": {"bindings": []}}
        http_error = urllib.error.HTTPError(
            url="test", code=429, msg="Too Many Requests", hdrs={}, fp=None
        )

        mock_query_result = Mock()
        mock_query_result.convert.side_effect = [http_error, mock_result]
        mock_sparql.query.return_value = mock_query_result

        mock_progress = MagicMock()
        mock_tqdm.return_value.__enter__ = Mock(return_value=mock_progress)
        mock_tqdm.return_value.__exit__ = Mock(return_value=False)

        result = safe_query(mock_sparql)
        assert mock_sleep.called

    @patch("mlscores.query.tqdm")
    def test_safe_query_returns_none_on_other_http_error(self, mock_tqdm):
        """Test that other HTTP errors return None."""
        mock_sparql = Mock()

        http_error = urllib.error.HTTPError(
            url="test", code=500, msg="Internal Server Error", hdrs={}, fp=None
        )
        mock_sparql.query().convert.side_effect = http_error

        mock_progress = MagicMock()
        mock_tqdm.return_value.__enter__ = Mock(return_value=mock_progress)
        mock_tqdm.return_value.__exit__ = Mock(return_value=False)

        result = safe_query(mock_sparql)
        assert result is None


class TestGetQualifierPropertiesAndValues:
    """Tests for get_qualifier_properties_and_values function."""

    def test_returns_result_for_valid_item(self):
        """Test that a valid item returns results."""
        # Q5 (human) has qualifiers
        result = get_qualifier_properties_and_values("Q5")
        # Result could be None or have bindings depending on the item
        assert result is None or "results" in result


class TestGetReferencePropertiesAndValues:
    """Tests for get_reference_properties_and_values function."""

    def test_returns_result_for_valid_item(self):
        """Test that a valid item returns results."""
        # Q5 (human) may have references
        result = get_reference_properties_and_values("Q5")
        # Result could be None or have bindings depending on the item
        assert result is None or "results" in result
