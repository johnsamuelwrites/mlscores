#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import pytest
from unittest.mock import patch, Mock, MagicMock
from io import StringIO

from mlscores.display import print_language_percentages, print_item_language_table
from mlscores.constants import WIKIDATA_PROPERTY_PREFIX, WIKIDATA_ENTITY_PREFIX


class TestPrintLanguagePercentages:
    """Tests for print_language_percentages function."""

    @patch("mlscores.display.Console")
    def test_empty_percentages(self, mock_console_class):
        """Test printing empty percentages dict."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        print_language_percentages({}, "Test Title")

        mock_console.print.assert_called_once()

    @patch("mlscores.display.Console")
    def test_single_language(self, mock_console_class):
        """Test printing single language percentage."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        percentages = {"en": 95.5}
        print_language_percentages(percentages, "Test Title")

        mock_console.print.assert_called_once()

    @patch("mlscores.display.Console")
    def test_multiple_languages(self, mock_console_class):
        """Test printing multiple language percentages."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        percentages = {"en": 95.5, "fr": 80.0, "es": 65.25}
        print_language_percentages(percentages, "Multiple Languages")

        mock_console.print.assert_called_once()

    @patch("mlscores.display.Console")
    def test_zero_percentage(self, mock_console_class):
        """Test printing zero percentages."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        percentages = {"en": 0.0, "fr": 0.0}
        print_language_percentages(percentages, "Zero Percentages")

        mock_console.print.assert_called_once()

    @patch("mlscores.display.Console")
    def test_hundred_percent(self, mock_console_class):
        """Test printing 100% percentages."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        percentages = {"en": 100.0}
        print_language_percentages(percentages, "Full Coverage")

        mock_console.print.assert_called_once()


class TestPrintItemLanguageTable:
    """Tests for print_item_language_table function."""

    @patch("mlscores.display.Console")
    def test_empty_data(self, mock_console_class):
        """Test printing empty data dict."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        print_item_language_table({}, "Test Title")

        mock_console.print.assert_called_once()

    @patch("mlscores.display.Console")
    def test_single_language_single_item(self, mock_console_class):
        """Test printing single language with single item."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        data = {"en": {"P31"}}
        print_item_language_table(data, "Single Item")

        mock_console.print.assert_called_once()

    @patch("mlscores.display.Console")
    def test_multiple_languages_multiple_items(self, mock_console_class):
        """Test printing multiple languages with multiple items."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        data = {
            "en": {"P31", "P21", "P569"},
            "fr": {"P31", "P21"},
            "es": {"P31"},
        }
        print_item_language_table(data, "Multiple Items")

        mock_console.print.assert_called_once()

    @patch("mlscores.display.Console")
    @patch("mlscores.display.Table")
    def test_uri_stripping_property_prefix(self, mock_table_class, mock_console_class):
        """Test that property URIs are properly stripped from display."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        mock_table = MagicMock()
        mock_table_class.return_value = mock_table

        data = {"en": {f"{WIKIDATA_PROPERTY_PREFIX}P31"}}
        print_item_language_table(data, "URI Stripping Test")

        # Check that add_row was called with stripped URI
        mock_table.add_row.assert_called_once()
        args, kwargs = mock_table.add_row.call_args
        # The items string should have the prefix stripped
        assert WIKIDATA_PROPERTY_PREFIX not in args[1]
        assert "P31" in args[1]

    @patch("mlscores.display.Console")
    @patch("mlscores.display.Table")
    def test_uri_stripping_entity_prefix(self, mock_table_class, mock_console_class):
        """Test that entity URIs are properly stripped from display."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        mock_table = MagicMock()
        mock_table_class.return_value = mock_table

        data = {"en": {f"{WIKIDATA_ENTITY_PREFIX}Q42"}}
        print_item_language_table(data, "Entity URI Stripping Test")

        mock_table.add_row.assert_called_once()
        args, kwargs = mock_table.add_row.call_args
        assert WIKIDATA_ENTITY_PREFIX not in args[1]
        assert "Q42" in args[1]

    @patch("mlscores.display.Console")
    def test_empty_set_for_language(self, mock_console_class):
        """Test printing language with empty item set."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        data = {"en": set()}
        print_item_language_table(data, "Empty Set")

        mock_console.print.assert_called_once()
