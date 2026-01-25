#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Output formatters for mlscores results."""

import json
import csv
from io import StringIO
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict, field


@dataclass
class MultilingualityResult:
    """Container for multilinguality calculation results."""

    item_id: str
    property_label_percentages: Dict[str, float]
    value_label_percentages: Dict[str, float]
    combined_percentages: Dict[str, float]
    missing_property_translations: Optional[Dict[str, List[str]]] = None
    missing_value_translations: Optional[Dict[str, List[str]]] = None


class OutputFormatter:
    """Base class for output formatters."""

    def format(self, results: List[MultilingualityResult]) -> str:
        """Format results to string output."""
        raise NotImplementedError


class JSONFormatter(OutputFormatter):
    """Format results as JSON."""

    def format(self, results: List[MultilingualityResult]) -> str:
        """Format results as pretty-printed JSON."""
        data = [asdict(r) for r in results]
        return json.dumps(data, indent=2, ensure_ascii=False)


class CSVFormatter(OutputFormatter):
    """Format results as CSV."""

    def format(self, results: List[MultilingualityResult]) -> str:
        """Format results as CSV with one row per item/category combination."""
        output = StringIO()

        if not results:
            return ""

        # Collect all languages across all results
        all_languages: Set[str] = set()
        for result in results:
            all_languages.update(result.combined_percentages.keys())

        all_languages_sorted = sorted(all_languages)

        writer = csv.writer(output)

        # Header
        header = ["item_id", "category"] + all_languages_sorted
        writer.writerow(header)

        for result in results:
            # Property labels row
            row = [result.item_id, "property_labels"]
            for lang in all_languages_sorted:
                row.append(f"{result.property_label_percentages.get(lang, 0):.2f}")
            writer.writerow(row)

            # Value labels row
            row = [result.item_id, "value_labels"]
            for lang in all_languages_sorted:
                row.append(f"{result.value_label_percentages.get(lang, 0):.2f}")
            writer.writerow(row)

            # Combined row
            row = [result.item_id, "combined"]
            for lang in all_languages_sorted:
                row.append(f"{result.combined_percentages.get(lang, 0):.2f}")
            writer.writerow(row)

        return output.getvalue()


class TableFormatter(OutputFormatter):
    """Format results as Rich tables (existing behavior)."""

    def format(self, results: List[MultilingualityResult]) -> str:
        """
        Format results using Rich tables.

        Note: This returns an empty string as the actual display
        is handled directly via the display module's console output.
        """
        from .display import print_language_percentages

        for result in results:
            print(f"\nFor Wikidata (Wikibase) item: {result.item_id}")
            print_language_percentages(
                result.property_label_percentages,
                "Language Percentages for property labels",
            )
            print_language_percentages(
                result.value_label_percentages,
                "Language Percentages for property value labels",
            )
            print_language_percentages(
                result.combined_percentages,
                "Combined Language Percentages for property label and property value labels",
            )

        return ""


def get_formatter(format_type: str) -> OutputFormatter:
    """
    Factory function to get appropriate formatter.

    Args:
        format_type: One of 'json', 'csv', or 'table'

    Returns:
        OutputFormatter instance

    Raises:
        ValueError: If format_type is not recognized
    """
    formatters = {
        "json": JSONFormatter(),
        "csv": CSVFormatter(),
        "table": TableFormatter(),
    }

    if format_type not in formatters:
        raise ValueError(
            f"Unknown format type: {format_type}. "
            f"Available: {list(formatters.keys())}"
        )

    return formatters[format_type]


def convert_sets_to_lists(data: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    """Convert a dict of sets to a dict of lists for JSON serialization."""
    return {k: sorted(list(v)) for k, v in data.items()}
