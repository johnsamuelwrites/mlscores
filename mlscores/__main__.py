#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import argparse
import sys
import time
from typing import List, Optional

from .display import print_language_percentages, print_item_language_table
from .query import (
    get_value_labels,
    get_properties_and_values,
    get_property_labels,
    get_qualifier_properties_and_values,
    get_reference_properties_and_values,
)
from .scores import (
    calculate_language_percentages,
    calculate_language_percentage_for_languages,
    get_properties_without_translations,
    get_properties_without_translations_in_languages,
)
from .formatters import (
    MultilingualityResult,
    get_formatter,
    convert_sets_to_lists,
)


def calculate_multilinguality_scores(
    identifiers: List[str],
    language_codes: Optional[List[str]] = None,
    missing: bool = False,
) -> List[MultilingualityResult]:
    """
    Calculate multilinguality scores based on identifiers and language codes.

    Args:
        identifiers: A list of Wikidata/Wikibase item identifiers.
        language_codes: A list of language codes to filter results. Defaults to None (all languages).
        missing: Whether to include missing translations in results.

    Returns:
        A list of MultilingualityResult objects containing the calculated scores.

    Notes:
        This function calculates the multilinguality scores of the Wikidata (or Wikibase) items
        and returns the values for the given language codes (by default: all available languages)
    """
    results: List[MultilingualityResult] = []

    for item_id in identifiers:
        # Step 1: Get properties and values
        properties_values_results = get_properties_and_values(item_id)
        qualifier_properties_values_results = get_qualifier_properties_and_values(
            item_id
        )
        reference_properties_values_results = get_reference_properties_and_values(
            item_id
        )

        if properties_values_results:
            if qualifier_properties_values_results:
                properties_values_results["results"]["bindings"] = (
                    properties_values_results["results"]["bindings"]
                    + qualifier_properties_values_results["results"]["bindings"]
                )
            if reference_properties_values_results:
                properties_values_results["results"]["bindings"] = (
                    properties_values_results["results"]["bindings"]
                    + reference_properties_values_results["results"]["bindings"]
                )
            property_value_pairs = [
                (result["property"]["value"], result["value"]["value"])
                for result in properties_values_results["results"]["bindings"]
            ]

            # Split property-value pairs into separate lists
            property_uris = list(
                set(pv[0] for pv in property_value_pairs)
            )  # Unique property URIs
            value_uris = list(
                set(pv[1] for pv in property_value_pairs if pv[1].startswith("http"))
            )  # Unique value URIs (IRIs)

            # Step 2: Get property labels
            property_labels_results = get_property_labels(property_uris)
            if language_codes is None:
                property_percentages = calculate_language_percentages(
                    property_labels_results
                )
            else:
                property_percentages = calculate_language_percentage_for_languages(
                    property_labels_results, language_codes
                )

            # Get missing property translations if requested
            missing_property_trans = None
            if missing:
                if language_codes is None:
                    missing_property_trans = convert_sets_to_lists(
                        get_properties_without_translations(property_labels_results)
                    )
                else:
                    missing_property_trans = convert_sets_to_lists(
                        get_properties_without_translations_in_languages(
                            property_labels_results, language_codes
                        )
                    )

            # Add a delay to avoid hitting the rate limit
            time.sleep(1)

            # Step 3: Get value labels
            value_labels_results = get_value_labels(value_uris)
            if language_codes is None:
                value_percentages = calculate_language_percentages(value_labels_results)
            else:
                value_percentages = calculate_language_percentage_for_languages(
                    value_labels_results, language_codes
                )

            # Get missing value translations if requested
            missing_value_trans = None
            if missing:
                if language_codes is None:
                    missing_value_trans = convert_sets_to_lists(
                        get_properties_without_translations(value_labels_results)
                    )
                else:
                    missing_value_trans = convert_sets_to_lists(
                        get_properties_without_translations_in_languages(
                            value_labels_results, language_codes
                        )
                    )

            # Step 4: Get combined results
            combined_results_list = property_labels_results + value_labels_results
            if language_codes is None:
                combined_percentages = calculate_language_percentages(
                    combined_results_list
                )
            else:
                combined_percentages = calculate_language_percentage_for_languages(
                    combined_results_list, language_codes
                )

            # Create result object
            result = MultilingualityResult(
                item_id=item_id,
                property_label_percentages=property_percentages,
                value_label_percentages=value_percentages,
                combined_percentages=combined_percentages,
                missing_property_translations=missing_property_trans,
                missing_value_translations=missing_value_trans,
            )
            results.append(result)

        else:
            # No properties found - create empty result
            empty_percentages = (
                {lang: 0.0 for lang in language_codes} if language_codes else {}
            )
            result = MultilingualityResult(
                item_id=item_id,
                property_label_percentages=empty_percentages,
                value_label_percentages=empty_percentages,
                combined_percentages=empty_percentages,
            )
            results.append(result)
            print(f"No properties and values found for item {item_id}.")

    return results


def output_results(
    results: List[MultilingualityResult],
    output_format: str = "table",
    output_file: Optional[str] = None,
    show_missing: bool = False,
) -> None:
    """
    Output results in the specified format.

    Args:
        results: List of MultilingualityResult objects.
        output_format: Output format ('table', 'json', or 'csv').
        output_file: Optional file path to write output to.
        show_missing: Whether to show missing translations (for table format).
    """
    formatter = get_formatter(output_format)

    if output_format == "table":
        # For table format, use direct console output
        for result in results:
            print(f"\nFor Wikidata (Wikibase) item: {result.item_id}")
            print_language_percentages(
                result.property_label_percentages,
                "Language Percentages for property labels",
            )
            if show_missing and result.missing_property_translations:
                # Convert lists back to sets for display
                missing_as_sets = {
                    k: set(v) for k, v in result.missing_property_translations.items()
                }
                print_item_language_table(
                    missing_as_sets, "Properties missing translation"
                )

            print_language_percentages(
                result.value_label_percentages,
                "Language Percentages for property value labels",
            )
            if show_missing and result.missing_value_translations:
                missing_as_sets = {
                    k: set(v) for k, v in result.missing_value_translations.items()
                }
                print_item_language_table(
                    missing_as_sets, "Property values missing translation"
                )

            print_language_percentages(
                result.combined_percentages,
                "Combined Language Percentages for property label and property value labels",
            )
    else:
        # For JSON/CSV formats, use formatter
        output = formatter.format(results)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Results written to {output_file}")
        else:
            print(output)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Calculate multilinguality scores for Wikidata/Wikibase items.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m mlscores Q42 -l en fr es
  python -m mlscores Q5 Q10 -l en fr -m
  python -m mlscores Q42 -f json -o results.json
  python -m mlscores Q42 -f csv -o results.csv
        """,
    )
    parser.add_argument(
        "identifiers",
        type=str,
        nargs="*",
        default=[],
        help="One or more Wikidata/Wikibase item identifiers (e.g., Q42, P31)",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        nargs="+",
        help="One or more language codes to filter results (e.g., en fr es)",
    )
    parser.add_argument(
        "-m",
        "--missing",
        action="store_true",
        help="Show properties missing translation",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file path (default: stdout)",
    )

    # Web server options
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start the web server instead of CLI mode",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Web server host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web server port (default: 8000)",
    )

    args = parser.parse_args()

    # Handle web server mode
    if args.web:
        try:
            from .web import run_server

            print(f"Starting web server at http://{args.host}:{args.port}")
            print(f"API documentation at http://{args.host}:{args.port}/api/docs")
            run_server(host=args.host, port=args.port)
        except ImportError:
            print(
                "Web dependencies not installed. Install with: pip install mlscores[web]"
            )
            sys.exit(1)
        return

    # Require identifiers for CLI mode
    if not args.identifiers:
        parser.error("the following arguments are required: identifiers")

    # Calculate scores
    results = calculate_multilinguality_scores(
        args.identifiers, args.language, args.missing
    )

    # Output results
    output_results(results, args.format, args.output, args.missing)


if __name__ == "__main__":
    main()
