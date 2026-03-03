#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
import time
import urllib
from typing import Any, Dict, List, Optional, Tuple

from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from tqdm import tqdm

from .constants import (
    DEFAULT_SPARQL_ENDPOINT,
    BATCH_SIZE,
    MAX_RETRIES,
    BACKOFF_MULTIPLIER,
    PROGRESS_BAR_TOTAL,
    WIKIDATA_PROPERTY_PREFIX,
    WIKIDATA_ITEM_PREFIX,
    DEFAULT_NO_LABEL,
    DEFAULT_UNKNOWN_LANGUAGE,
)
import importlib.util
from pathlib import Path

_BUILDERS_PATH = Path(__file__).parent / "web" / "static" / "wasm" / "query_builders.py"
_SPEC = importlib.util.spec_from_file_location("mlscores_query_builders", _BUILDERS_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load shared query builders from {_BUILDERS_PATH}")
_query_builders = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_query_builders)

build_properties_and_values_query = _query_builders.build_properties_and_values_query
build_qualifier_properties_and_values_query = _query_builders.build_qualifier_properties_and_values_query
build_reference_properties_and_values_query = _query_builders.build_reference_properties_and_values_query
build_property_labels_query = _query_builders.build_property_labels_query
build_value_labels_query = _query_builders.build_value_labels_query

# Wikidata SPARQL endpoint
user_agent = "WDQS-mlscores Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
sparql = SPARQLWrapper(DEFAULT_SPARQL_ENDPOINT, agent=user_agent)


def get_properties_and_values(item_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve properties and values for a given Wikidata item.

    This function takes a Wikidata item ID and returns its properties and values using a SPARQL query.

    Args:
        item_id (str): The ID of the Wikidata item to retrieve properties for.

    Returns:
        The result of the SPARQL query, or None if the query fails.

    Notes:
        This function uses the `safe_query` function to execute the SPARQL query with retry mechanism.
    """
    sparql.setQuery(build_properties_and_values_query(item_id))
    sparql.setReturnFormat(JSON)

    # Execute the query with retry mechanism
    return safe_query(sparql)


def get_qualifier_properties_and_values(item_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve qualifier properties and values for a given Wikidata item.

    This function takes a Wikidata item ID and returns its qualifier properties and values using a SPARQL query.

    Args:
        item_id (str): The ID of the Wikidata item to retrieve properties for.

    Returns:
        The result of the SPARQL query, or None if the query fails.

    Notes:
        This function uses the `safe_query` function to execute the SPARQL query with retry mechanism.
    """
    sparql.setQuery(build_qualifier_properties_and_values_query(item_id))
    sparql.setReturnFormat(JSON)

    # Execute the query with retry mechanism
    return safe_query(sparql)


def get_reference_properties_and_values(item_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve reference properties and values for a given Wikidata item.

    This function takes a Wikidata item ID and returns its reference properties and values using a SPARQL query.

    Args:
        item_id (str): The ID of the Wikidata item to retrieve properties for.

    Returns:
        The result of the SPARQL query, or None if the query fails.

    Notes:
        This function uses the `safe_query` function to execute the SPARQL query with retry mechanism.
    """
    sparql.setQuery(build_reference_properties_and_values_query(item_id))
    sparql.setReturnFormat(JSON)

    # Execute the query with retry mechanism
    return safe_query(sparql)


def get_property_labels(property_uris: List[str]) -> List[Tuple[str, str, str]]:
    """
    Retrieve labels for a list of property URIs.

    This function takes a list of property URIs and returns their corresponding labels and languages.

    Args:
        property_uris (list): A list of property URIs.

    Returns:
        A list of tuples containing the property URI, label, and language.

    Notes:
        This function uses the `safe_query` function to execute SPARQL queries with retry mechanism.
        It also uses a batch processing approach to handle large lists of property URIs.
    """
    # Filter out non-Wikidata property URIs
    filtered_uris = {
        uri
        for uri in property_uris
        if uri.startswith(WIKIDATA_PROPERTY_PREFIX)
    }

    # Convert the set to a list for easier processing
    filtered_uris = list(filtered_uris)

    # Initialize an empty list to store the results
    results = []

    # Process the property URIs in batches
    for i in range(0, len(filtered_uris), BATCH_SIZE):
        # Get the current batch of property URIs
        batch = filtered_uris[i : i + BATCH_SIZE]

        # Create the SPARQL query
        query = build_property_labels_query(batch)

        # Execute the query with retry mechanism
        sparql.setQuery(query)
        batch_results = safe_query(sparql)

        # Add the results to the list if the query was successful
        if batch_results:
            results.extend(batch_results["results"]["bindings"])

    # Return a list of tuples: (property, label, language)
    return [
        (
            result["p"]["value"],
            result.get("propertyLabel", {}).get("value", DEFAULT_NO_LABEL),
            result.get("propertyLabelLang", {}).get("value", DEFAULT_UNKNOWN_LANGUAGE),
        )
        for result in results
    ]


def get_value_labels(value_uris: List[str]) -> List[Tuple[str, str, str]]:
    """
    Retrieve labels for a list of value URIs.

    This function takes a list of value URIs and returns their corresponding labels and languages.

    Args:
        value_uris (list): A list of value URIs.

    Returns:
        A list of tuples containing the value URI, label, and language.

    Notes:
        This function uses the `safe_query` function to execute SPARQL queries with retry mechanism.
        It also uses a batch processing approach to handle large lists of value URIs.
    """
    # Filter out non-Wikidata value URIs
    filtered_uris = {
        uri for uri in value_uris if uri.startswith(WIKIDATA_ITEM_PREFIX)
    }

    # Convert the set to a list for easier processing
    filtered_uris = list(filtered_uris)

    # Initialize an empty list to store the results
    results = []

    # Process the value URIs in batches
    for i in range(0, len(filtered_uris), BATCH_SIZE):
        # Get the current batch of value URIs
        batch = filtered_uris[i : i + BATCH_SIZE]

        # Create the SPARQL query
        query = build_value_labels_query(batch)

        # Execute the query with retry mechanism
        sparql.setQuery(query)
        batch_results = safe_query(sparql)

        # Add the results to the list if the query was successful
        if batch_results:
            results.extend(batch_results["results"]["bindings"])

    # Return a list of tuples: (value, label, language)
    return [
        (
            result["v"]["value"],
            result.get("valueLabel", {}).get("value", DEFAULT_NO_LABEL),
            result.get("valueLabelLang", {}).get("value", DEFAULT_UNKNOWN_LANGUAGE),
        )
        for result in results
    ]


def safe_query(sparql: SPARQLWrapper) -> Optional[Dict[str, Any]]:
    """
    Execute a SPARQL query with retry mechanism.

    This function takes a SPARQL query object and attempts to execute it, retrying up to a maximum
    number of times if the query fails due to a rate limit or other transient errors.

    Args:
        sparql: A SPARQL query object.

    Returns:
        The result of the query, or None if the query fails after the maximum number of retries.

    Notes:
        This function uses an exponential backoff strategy to retry the query if it is rate-limited.
    """
    for attempt in range(MAX_RETRIES):
        try:
            # Show progress while waiting for the query to complete
            with tqdm(
                total=PROGRESS_BAR_TOTAL,
                desc="Querying",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                ncols=100,
            ) as progress_bar:
                # Execute the query
                result = sparql.query().convert()
                # Update the progress bar to complete
                progress_bar.update(PROGRESS_BAR_TOTAL)
                return result

        except urllib.error.HTTPError as e:
            # Handle rate limit errors
            if e.code == 429:
                # Exponential backoff
                wait_time = BACKOFF_MULTIPLIER**attempt
                print(f"Rate limit hit, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # Handle other HTTP errors
                print(f"HTTP error: {e}")
                break

        except SPARQLExceptions.QueryBadFormed as e:
            # Handle query syntax errors
            print(f"QueryBadFormed error: {e}")
            print(sparql)
            break

    # If all retries fail, return None
    return None
