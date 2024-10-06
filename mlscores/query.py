#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import time
import urllib
import re
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from tqdm import tqdm  # Import tqdm for the progress bar
from .scores import calculate_language_percentage

# Wikidata SPARQL endpoint
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")


def get_properties_and_values(item_id):
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
    sparql.setQuery(
        f"""
    SELECT?p?v WHERE {{
      wd:{item_id}?p?v.
    }}
    """
    )
    sparql.setReturnFormat(JSON)

    # Execute the query with retry mechanism
    return safe_query(sparql)


def get_property_labels(property_uris):
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
        if uri.startswith("http://www.wikidata.org/prop/direct/")
    }

    # Convert the set to a list for easier processing
    filtered_uris = list(filtered_uris)

    # Define the batch size for processing
    batch_size = 100  # Adjust this size as needed

    # Initialize an empty list to store the results
    results = []

    # Process the property URIs in batches
    for i in range(0, len(filtered_uris), batch_size):
        # Get the current batch of property URIs
        batch = filtered_uris[i : i + batch_size]

        # Create a VALUES clause for the SPARQL query
        values_clause = " ".join([f"(<{uri}>)" for uri in batch])

        # Create the SPARQL query
        query = f"""
        SELECT?p?propertyLabel?propertyLabelLang WHERE {{
          VALUES (?p) {{ {values_clause} }}

          OPTIONAL {{
           ?property wikibase:directClaim?p;
                      rdfs:label?propertyLabel.
            BIND(LANG(?propertyLabel) AS?propertyLabelLang).
          }}
        }}
        """

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
            result.get("propertyLabel", {}).get("value", "No label"),
            result.get("propertyLabelLang", {}).get("value", "Unknown language"),
        )
        for result in results
    ]

    # Return a list of tuples: (property, label, language)
    return [
        (
            result["p"]["value"],
            result.get("propertyLabel", {}).get("value", "No label"),
            result.get("propertyLabelLang", {}).get("value", "Unknown language"),
        )
        for result in results
    ]


def get_value_labels(value_uris):
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
        uri for uri in value_uris if uri.startswith("http://www.wikidata.org/entity/Q")
    }

    # Convert the set to a list for easier processing
    filtered_uris = list(filtered_uris)

    # Define the batch size for processing
    batch_size = 100  # Adjust this size as needed

    # Initialize an empty list to store the results
    results = []

    # Process the value URIs in batches
    for i in range(0, len(filtered_uris), batch_size):
        # Get the current batch of value URIs
        batch = filtered_uris[i : i + batch_size]

        # Create a VALUES clause for the SPARQL query
        values_clause = " ".join([f"(<{uri}>)" for uri in batch])

        # Create the SPARQL query
        query = f"""
        SELECT?v?valueLabel?valueLabelLang WHERE {{
          VALUES (?v) {{ {values_clause} }}

          OPTIONAL {{
            FILTER(isIRI(?v)).
           ?v rdfs:label?valueLabel.
            BIND(LANG(?valueLabel) AS?valueLabelLang).
          }}
        }}
        """

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
            result.get("valueLabel", {}).get("value", "No label"),
            result.get("valueLabelLang", {}).get("value", "Unknown language"),
        )
        for result in results
    ]


def safe_query(sparql):
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
    max_retries = 5

    for attempt in range(max_retries):
        try:
            # Show progress while waiting for the query to complete
            with tqdm(
                total=100,
                desc="Querying",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                ncols=100,
            ) as progress_bar:
                # Execute the query
                result = sparql.query().convert()
                # Update the progress bar to complete
                progress_bar.update(100)
                return result

        except urllib.error.HTTPError as e:
            # Handle rate limit errors
            if e.code == 429:
                # Exponential backoff
                wait_time = 2**attempt
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
