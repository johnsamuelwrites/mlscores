#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Pydantic models for API request/response validation."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MultilingualityRequest(BaseModel):
    """Request model for multilinguality score calculation."""

    identifiers: List[str] = Field(
        ...,
        description="List of Wikidata/Wikibase item identifiers (e.g., ['Q42', 'Q5'])",
        min_length=1,
        max_length=100,
    )
    languages: Optional[List[str]] = Field(
        None, description="List of language codes to filter results (e.g., ['en', 'fr'])"
    )
    include_missing: bool = Field(
        False, description="Include list of properties missing translations"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "identifiers": ["Q42", "Q5"],
                "languages": ["en", "fr", "es"],
                "include_missing": True,
            }
        }
    }


class LanguagePercentages(BaseModel):
    """Language percentages for a specific category."""

    percentages: Dict[str, float] = Field(
        ..., description="Map of language code to percentage"
    )


class MissingTranslations(BaseModel):
    """Missing translations for an item."""

    by_language: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of language code to list of missing property URIs",
    )


class ItemResult(BaseModel):
    """Result for a single Wikidata item."""

    item_id: str = Field(..., description="Wikidata item identifier")
    property_labels: LanguagePercentages
    value_labels: LanguagePercentages
    combined: LanguagePercentages
    missing_property_translations: Optional[MissingTranslations] = None
    missing_value_translations: Optional[MissingTranslations] = None


class MultilingualityResponse(BaseModel):
    """Response model for multilinguality score calculation."""

    success: bool = True
    results: List[ItemResult]

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "results": [
                    {
                        "item_id": "Q42",
                        "property_labels": {"percentages": {"en": 99.5, "fr": 95.0}},
                        "value_labels": {"percentages": {"en": 98.0, "fr": 90.0}},
                        "combined": {"percentages": {"en": 98.75, "fr": 92.5}},
                    }
                ],
            }
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = False
    error: str
    details: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str
    cache_enabled: bool
    endpoint: str
