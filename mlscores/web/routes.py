#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""FastAPI route definitions."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from .models import (
    MultilingualityRequest,
    MultilingualityResponse,
    ItemResult,
    LanguagePercentages,
    MissingTranslations,
    ErrorResponse,
    HealthResponse,
)
from ..query import (
    get_properties_and_values,
    get_qualifier_properties_and_values,
    get_reference_properties_and_values,
    get_property_labels,
    get_value_labels,
)
from ..scores import (
    calculate_language_percentages,
    calculate_language_percentage_for_languages,
    get_properties_without_translations,
    get_properties_without_translations_in_languages,
)
from ..cache import get_cache
from ..constants import DEFAULT_SPARQL_ENDPOINT

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API health status."""
    cache = get_cache()

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        cache_enabled=cache.enabled,
        endpoint=DEFAULT_SPARQL_ENDPOINT,
    )


@router.post(
    "/scores",
    response_model=MultilingualityResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Scores"],
    summary="Calculate multilinguality scores",
    description="Calculate multilinguality scores for one or more Wikidata items.",
)
async def calculate_scores(request: MultilingualityRequest):
    """
    Calculate multilinguality scores for Wikidata items.

    - **identifiers**: List of Wikidata item IDs (e.g., Q42, Q5)
    - **languages**: Optional list of language codes to filter results
    - **include_missing**: Include missing translation details
    """
    results = []

    for item_id in request.identifiers:
        try:
            item_result = _calculate_item_scores(
                item_id, request.languages, request.include_missing
            )
            results.append(item_result)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing {item_id}: {str(e)}"
            )

    return MultilingualityResponse(success=True, results=results)


@router.get(
    "/scores/{item_id}",
    response_model=ItemResult,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Scores"],
    summary="Get scores for a single item",
)
async def get_item_scores(
    item_id: str,
    languages: Optional[List[str]] = Query(None),
    include_missing: bool = Query(False),
):
    """
    Get multilinguality scores for a single Wikidata item.

    - **item_id**: Wikidata item ID (e.g., Q42)
    - **languages**: Optional language codes to filter results
    - **include_missing**: Include missing translation details
    """
    try:
        return _calculate_item_scores(item_id, languages, include_missing)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


def _calculate_item_scores(
    item_id: str,
    languages: Optional[List[str]],
    include_missing: bool,
) -> ItemResult:
    """Internal function to calculate scores for an item."""

    # Get properties and values
    properties_values = get_properties_and_values(item_id)

    if not properties_values:
        raise ValueError(f"No properties found for item {item_id}")

    # Get qualifier and reference properties
    qualifier_results = get_qualifier_properties_and_values(item_id)
    reference_results = get_reference_properties_and_values(item_id)

    # Combine results
    bindings = properties_values["results"]["bindings"]
    if qualifier_results:
        bindings.extend(qualifier_results["results"]["bindings"])
    if reference_results:
        bindings.extend(reference_results["results"]["bindings"])

    # Extract URIs
    property_value_pairs = [
        (result["property"]["value"], result["value"]["value"]) for result in bindings
    ]

    property_uris = list(set(pv[0] for pv in property_value_pairs))
    value_uris = list(
        set(pv[1] for pv in property_value_pairs if pv[1].startswith("http"))
    )

    # Get labels
    property_labels_results = get_property_labels(property_uris)
    value_labels_results = get_value_labels(value_uris)

    # Calculate percentages
    if languages:
        prop_percentages = calculate_language_percentage_for_languages(
            property_labels_results, languages
        )
        value_percentages = calculate_language_percentage_for_languages(
            value_labels_results, languages
        )
        combined_results = property_labels_results + value_labels_results
        combined_percentages = calculate_language_percentage_for_languages(
            combined_results, languages
        )
    else:
        prop_percentages = calculate_language_percentages(property_labels_results)
        value_percentages = calculate_language_percentages(value_labels_results)
        combined_results = property_labels_results + value_labels_results
        combined_percentages = calculate_language_percentages(combined_results)

    # Build result
    result = ItemResult(
        item_id=item_id,
        property_labels=LanguagePercentages(percentages=prop_percentages),
        value_labels=LanguagePercentages(percentages=value_percentages),
        combined=LanguagePercentages(percentages=combined_percentages),
    )

    # Add missing translations if requested
    if include_missing:
        if languages:
            prop_missing = get_properties_without_translations_in_languages(
                property_labels_results, languages
            )
            value_missing = get_properties_without_translations_in_languages(
                value_labels_results, languages
            )
        else:
            prop_missing = get_properties_without_translations(property_labels_results)
            value_missing = get_properties_without_translations(value_labels_results)

        # Convert sets to lists for JSON serialization
        result.missing_property_translations = MissingTranslations(
            by_language={k: sorted(list(v)) for k, v in prop_missing.items()}
        )
        result.missing_value_translations = MissingTranslations(
            by_language={k: sorted(list(v)) for k, v in value_missing.items()}
        )

    return result
