#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import pytest
from unittest.mock import patch, Mock
from io import StringIO

from mlscores.__main__ import calculate_multilinguality_scores, output_results
from mlscores.formatters import MultilingualityResult


class TestCalculateMultilingualityScores:
    """Tests for the main calculation function."""

    @patch("mlscores.__main__.get_properties_and_values")
    @patch("mlscores.__main__.get_qualifier_properties_and_values")
    @patch("mlscores.__main__.get_reference_properties_and_values")
    @patch("mlscores.__main__.get_property_labels")
    @patch("mlscores.__main__.get_value_labels")
    @patch("mlscores.__main__.time.sleep")
    def test_basic_calculation(
        self,
        mock_sleep,
        mock_value_labels,
        mock_prop_labels,
        mock_ref,
        mock_qual,
        mock_props,
    ):
        """Test basic calculation flow returns results."""
        mock_props.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P31"
                        },
                        "value": {"value": "http://www.wikidata.org/entity/Q5"},
                    }
                ]
            }
        }
        mock_qual.return_value = None
        mock_ref.return_value = None
        mock_prop_labels.return_value = [
            ("http://www.wikidata.org/prop/direct/P31", "instance of", "en")
        ]
        mock_value_labels.return_value = [
            ("http://www.wikidata.org/entity/Q5", "human", "en")
        ]

        results = calculate_multilinguality_scores(["Q42"])

        assert len(results) == 1
        assert results[0].item_id == "Q42"
        assert "en" in results[0].property_label_percentages
        assert "en" in results[0].value_label_percentages
        assert "en" in results[0].combined_percentages

    @patch("mlscores.__main__.get_properties_and_values")
    def test_no_properties_found(self, mock_props, capsys):
        """Test handling when no properties are found."""
        mock_props.return_value = None

        results = calculate_multilinguality_scores(["Q999999999"])

        captured = capsys.readouterr()
        assert "No properties and values found" in captured.out
        assert len(results) == 1
        assert results[0].item_id == "Q999999999"

    @patch("mlscores.__main__.get_properties_and_values")
    @patch("mlscores.__main__.get_qualifier_properties_and_values")
    @patch("mlscores.__main__.get_reference_properties_and_values")
    @patch("mlscores.__main__.get_property_labels")
    @patch("mlscores.__main__.get_value_labels")
    @patch("mlscores.__main__.time.sleep")
    def test_with_language_codes(
        self,
        mock_sleep,
        mock_value_labels,
        mock_prop_labels,
        mock_ref,
        mock_qual,
        mock_props,
    ):
        """Test calculation with specific language codes."""
        mock_props.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P31"
                        },
                        "value": {"value": "http://www.wikidata.org/entity/Q5"},
                    }
                ]
            }
        }
        mock_qual.return_value = None
        mock_ref.return_value = None
        mock_prop_labels.return_value = [
            ("http://www.wikidata.org/prop/direct/P31", "instance of", "en"),
            ("http://www.wikidata.org/prop/direct/P31", "instance de", "fr"),
        ]
        mock_value_labels.return_value = [
            ("http://www.wikidata.org/entity/Q5", "human", "en"),
            ("http://www.wikidata.org/entity/Q5", "humain", "fr"),
        ]

        results = calculate_multilinguality_scores(["Q42"], language_codes=["en", "fr"])

        assert len(results) == 1
        # Should only have en and fr in results
        assert "en" in results[0].combined_percentages
        assert "fr" in results[0].combined_percentages

    @patch("mlscores.__main__.get_properties_and_values")
    @patch("mlscores.__main__.get_qualifier_properties_and_values")
    @patch("mlscores.__main__.get_reference_properties_and_values")
    @patch("mlscores.__main__.get_property_labels")
    @patch("mlscores.__main__.get_value_labels")
    @patch("mlscores.__main__.time.sleep")
    def test_with_missing_flag(
        self,
        mock_sleep,
        mock_value_labels,
        mock_prop_labels,
        mock_ref,
        mock_qual,
        mock_props,
    ):
        """Test calculation with missing translations flag."""
        mock_props.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P31"
                        },
                        "value": {"value": "http://www.wikidata.org/entity/Q5"},
                    }
                ]
            }
        }
        mock_qual.return_value = None
        mock_ref.return_value = None
        mock_prop_labels.return_value = [
            ("http://www.wikidata.org/prop/direct/P31", "instance of", "en")
        ]
        mock_value_labels.return_value = [
            ("http://www.wikidata.org/entity/Q5", "human", "en")
        ]

        results = calculate_multilinguality_scores(["Q42"], missing=True)

        assert len(results) == 1
        # Missing translations should be populated (may be empty dict if no missing)
        assert results[0].missing_property_translations is not None
        assert results[0].missing_value_translations is not None

    @patch("mlscores.__main__.get_properties_and_values")
    @patch("mlscores.__main__.get_qualifier_properties_and_values")
    @patch("mlscores.__main__.get_reference_properties_and_values")
    @patch("mlscores.__main__.get_property_labels")
    @patch("mlscores.__main__.get_value_labels")
    @patch("mlscores.__main__.time.sleep")
    def test_multiple_items(
        self,
        mock_sleep,
        mock_value_labels,
        mock_prop_labels,
        mock_ref,
        mock_qual,
        mock_props,
    ):
        """Test calculation with multiple items."""
        mock_props.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P31"
                        },
                        "value": {"value": "http://www.wikidata.org/entity/Q5"},
                    }
                ]
            }
        }
        mock_qual.return_value = None
        mock_ref.return_value = None
        mock_prop_labels.return_value = [
            ("http://www.wikidata.org/prop/direct/P31", "instance of", "en")
        ]
        mock_value_labels.return_value = [
            ("http://www.wikidata.org/entity/Q5", "human", "en")
        ]

        results = calculate_multilinguality_scores(["Q42", "Q5"])

        assert len(results) == 2
        assert results[0].item_id == "Q42"
        assert results[1].item_id == "Q5"

    @patch("mlscores.__main__.get_properties_and_values")
    @patch("mlscores.__main__.get_qualifier_properties_and_values")
    @patch("mlscores.__main__.get_reference_properties_and_values")
    @patch("mlscores.__main__.get_property_labels")
    @patch("mlscores.__main__.get_value_labels")
    @patch("mlscores.__main__.time.sleep")
    def test_includes_qualifier_results(
        self,
        mock_sleep,
        mock_value_labels,
        mock_prop_labels,
        mock_ref,
        mock_qual,
        mock_props,
    ):
        """Test that qualifier results are included."""
        mock_props.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P31"
                        },
                        "value": {"value": "http://www.wikidata.org/entity/Q5"},
                    }
                ]
            }
        }
        mock_qual.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P580"
                        },
                        "value": {"value": "2020-01-01"},
                    }
                ]
            }
        }
        mock_ref.return_value = None
        mock_prop_labels.return_value = [
            ("http://www.wikidata.org/prop/direct/P31", "instance of", "en"),
            ("http://www.wikidata.org/prop/direct/P580", "start time", "en"),
        ]
        mock_value_labels.return_value = [
            ("http://www.wikidata.org/entity/Q5", "human", "en")
        ]

        results = calculate_multilinguality_scores(["Q42"])

        # Verify that prop_labels was called with combined URIs
        assert mock_prop_labels.called
        assert len(results) == 1

    @patch("mlscores.__main__.get_properties_and_values")
    @patch("mlscores.__main__.get_qualifier_properties_and_values")
    @patch("mlscores.__main__.get_reference_properties_and_values")
    @patch("mlscores.__main__.get_property_labels")
    @patch("mlscores.__main__.get_value_labels")
    @patch("mlscores.__main__.time.sleep")
    def test_includes_reference_results(
        self,
        mock_sleep,
        mock_value_labels,
        mock_prop_labels,
        mock_ref,
        mock_qual,
        mock_props,
    ):
        """Test that reference results are included."""
        mock_props.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P31"
                        },
                        "value": {"value": "http://www.wikidata.org/entity/Q5"},
                    }
                ]
            }
        }
        mock_qual.return_value = None
        mock_ref.return_value = {
            "results": {
                "bindings": [
                    {
                        "property": {
                            "value": "http://www.wikidata.org/prop/direct/P248"
                        },
                        "value": {
                            "value": "http://www.wikidata.org/entity/Q36578"
                        },
                    }
                ]
            }
        }
        mock_prop_labels.return_value = [
            ("http://www.wikidata.org/prop/direct/P31", "instance of", "en"),
            ("http://www.wikidata.org/prop/direct/P248", "stated in", "en"),
        ]
        mock_value_labels.return_value = [
            ("http://www.wikidata.org/entity/Q5", "human", "en"),
            ("http://www.wikidata.org/entity/Q36578", "GND", "en"),
        ]

        results = calculate_multilinguality_scores(["Q42"])

        assert mock_prop_labels.called
        assert mock_value_labels.called
        assert len(results) == 1


class TestOutputResults:
    """Tests for the output_results function."""

    def test_output_json_format(self, capsys):
        """Test JSON output format."""
        results = [
            MultilingualityResult(
                item_id="Q42",
                property_label_percentages={"en": 100.0},
                value_label_percentages={"en": 100.0},
                combined_percentages={"en": 100.0},
            )
        ]

        output_results(results, output_format="json")

        captured = capsys.readouterr()
        assert '"item_id": "Q42"' in captured.out
        assert '"en": 100.0' in captured.out

    def test_output_csv_format(self, capsys):
        """Test CSV output format."""
        results = [
            MultilingualityResult(
                item_id="Q42",
                property_label_percentages={"en": 100.0},
                value_label_percentages={"en": 100.0},
                combined_percentages={"en": 100.0},
            )
        ]

        output_results(results, output_format="csv")

        captured = capsys.readouterr()
        assert "item_id" in captured.out
        assert "Q42" in captured.out

    @patch("mlscores.__main__.print_language_percentages")
    def test_output_table_format(self, mock_print):
        """Test table output format."""
        results = [
            MultilingualityResult(
                item_id="Q42",
                property_label_percentages={"en": 100.0},
                value_label_percentages={"en": 100.0},
                combined_percentages={"en": 100.0},
            )
        ]

        output_results(results, output_format="table")

        # Table format should call print_language_percentages 3 times per item
        assert mock_print.call_count == 3
