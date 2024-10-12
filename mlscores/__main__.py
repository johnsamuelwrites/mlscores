#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import argparse
import time
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from tqdm import tqdm  # Import tqdm for the progress bar

from .display import print_language_percentages
from .query import (
    get_value_labels,
    get_properties_and_values,
    get_property_labels,
    get_qualifier_properties_and_values,
    get_reference_properties_and_values,
)
from .scores import (
    calculate_language_percentage,
    calculate_language_percentages,
    calculate_language_percentage_for_languages,
)


def calculate_multilinguality_scores(identifiers, language_codes=None):
    """
    Calculate multilinguality scores based on identifiers and language codes.

    Args:
        identifiers (list): A list of identifiers.
        language_codes (list, optional): A list of language codes. Defaults to None.

    Returns:
        None

    Notes:
        This function calculates the multilinguality scores of the Wikidata (or Wikibase) items
        and prints the values for the given language codes (by default: all available languages)
    """
    for item_id in identifiers:
        print("For Wikidata (Wikibase) item:", item_id)

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
            percentages = None
            property_labels_results = get_property_labels(property_uris)
            if language_codes is None:
                percentages = calculate_language_percentages(property_labels_results)
            else:
                percentages = calculate_language_percentage_for_languages(
                    property_labels_results, language_codes
                )
            print_language_percentages(
                percentages, "Language Percentages for property labels"
            )

            # Add a delay to avoid hitting the rate limit
            time.sleep(1)  # Sleep for 1 second

            # Step 3: Get value labels
            value_labels_results = get_value_labels(value_uris)
            if language_codes is None:
                percentages = calculate_language_percentages(value_labels_results)
            else:
                percentages = calculate_language_percentage_for_languages(
                    value_labels_results, language_codes
                )
            print_language_percentages(
                percentages, "Language Percentages for property value labels"
            )

            # Step 4: Get combined results
            combined_results = []
            combined_results = combined_results + property_labels_results
            combined_results = combined_results + value_labels_results
            if language_codes is None:
                percentages = calculate_language_percentages(combined_results)
            else:
                percentages = calculate_language_percentage_for_languages(
                    combined_results, language_codes
                )
            print_language_percentages(
                percentages,
                "Combined Language Percentages for property label and property value labels",
            )

        else:
            print("No properties and values found for the item.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process identifiers and language codes."
    )
    parser.add_argument(
        "identifiers", type=str, nargs="+", help="One or more identifiers"
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        nargs="+",
        help="One or more language codes (en, fr, ...)",
    )

    args = parser.parse_args()

    calculate_multilinguality_scores(args.identifiers, args.language)
