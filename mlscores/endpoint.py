#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""SPARQL endpoint configuration for custom Wikibase instances."""

import base64
from dataclasses import dataclass
from typing import Optional

from .constants import (
    DEFAULT_SPARQL_ENDPOINT,
    WIKIDATA_PROPERTY_PREFIX,
    WIKIDATA_ENTITY_PREFIX,
    WIKIDATA_ITEM_PREFIX,
)


@dataclass
class EndpointConfig:
    """Configuration for a SPARQL endpoint."""

    url: str = DEFAULT_SPARQL_ENDPOINT
    property_prefix: str = WIKIDATA_PROPERTY_PREFIX
    entity_prefix: str = WIKIDATA_ENTITY_PREFIX
    item_prefix: str = WIKIDATA_ITEM_PREFIX
    username: Optional[str] = None
    password: Optional[str] = None

    @property
    def auth_header(self) -> Optional[str]:
        """Generate Basic Auth header if credentials are provided."""
        if self.username and self.password:
            credentials = f"{self.username}:{self.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return f"Basic {encoded}"
        return None

    def is_wikidata(self) -> bool:
        """Check if this is the default Wikidata endpoint."""
        return self.url == DEFAULT_SPARQL_ENDPOINT


# Predefined configurations for known Wikibase instances
KNOWN_ENDPOINTS = {
    "wikidata": EndpointConfig(),
    "commons": EndpointConfig(
        url="https://wcqs-beta.wmflabs.org/sparql",
        property_prefix="http://www.wikidata.org/prop/direct/",
        entity_prefix="http://commons.wikimedia.org/entity/",
        item_prefix="http://commons.wikimedia.org/entity/M",
    ),
}


def create_endpoint_config(
    url: Optional[str] = None,
    property_prefix: Optional[str] = None,
    entity_prefix: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> EndpointConfig:
    """
    Create an endpoint configuration.

    Args:
        url: SPARQL endpoint URL
        property_prefix: URI prefix for properties
        entity_prefix: URI prefix for entities
        username: Username for basic auth
        password: Password for basic auth

    Returns:
        EndpointConfig instance
    """
    config = EndpointConfig()

    if url is not None:
        config.url = url

    if property_prefix is not None:
        config.property_prefix = property_prefix

    if entity_prefix is not None:
        config.entity_prefix = entity_prefix
        # Item prefix is typically entity prefix + "Q" for Wikidata-like instances
        if not entity_prefix.endswith("/"):
            config.item_prefix = entity_prefix + "/Q"
        else:
            config.item_prefix = entity_prefix + "Q"

    config.username = username
    config.password = password

    return config


def get_known_endpoint(name: str) -> Optional[EndpointConfig]:
    """
    Get a predefined endpoint configuration by name.

    Args:
        name: Name of the known endpoint (e.g., 'wikidata', 'commons')

    Returns:
        EndpointConfig if found, None otherwise
    """
    return KNOWN_ENDPOINTS.get(name.lower())
