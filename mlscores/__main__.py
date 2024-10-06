#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import argparse
import time
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from tqdm import tqdm  # Import tqdm for the progress bar

from .query import get_value_labels, get_properties_and_values, get_property_labels
from .scores import calculate_language_percentage


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
        and prints the values for the given language codes (by default: en)
    """
    if language_codes is None:
        language_codes = ["en"]

    for item_id in identifiers:
        print("For Wikidata (Wikibase) item:", item_id)

        # Step 1: Get properties and values
        properties_values_results = get_properties_and_values(item_id)

        if properties_values_results:
            property_value_pairs = [
                (result["p"]["value"], result["v"]["value"])
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
            language = "ml"
            property_labels_results = get_property_labels(property_uris)
            for language in language_codes:
                percentage = calculate_language_percentage(
                    property_labels_results, language
                )
                print(
                    f"The percentage of properties in {language} is {percentage:.2f}%"
                )

            # Add a delay to avoid hitting the rate limit
            time.sleep(1)  # Sleep for 1 second

            # Step 3: Get value labels
            value_labels_results = get_value_labels(value_uris)
            for language in language_codes:
                percentage = calculate_language_percentage(
                    value_labels_results, language
                )
                print(
                    f"The percentage of property values in {language} is {percentage:.2f}%"
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
